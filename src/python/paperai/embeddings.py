"""
Embeddings module
"""

import os
import os.path
import pickle
import tempfile

from errno import ENOENT
from multiprocessing import Pool

import faiss
import numpy as np

from pymagnitude import Magnitude
from sklearn.decomposition import TruncatedSVD

from .scoring import Scoring

# Multiprocessing helper methods
# pylint: disable=W0603
EMBEDDINGS = None

def create(config, scoring):
    """
    Multiprocessing helper method. Creates a global embeddings object to be accessed in a new
    subprocess.

    Args:
        config: configuration
        scoring: scoring instance
    """

    global EMBEDDINGS

    # Create a global embedding object using configuration and saved
    EMBEDDINGS = Embeddings(config)

    # Copy scoring object
    EMBEDDINGS.scoring = scoring

def transform(document):
    """
    Multiprocessing helper method. Transforms document tokens into an embedding.

    Args:
        document: (id, tokens, tags)

    Returns:
        (id, embedding)
    """

    global EMBEDDINGS

    return (document[0], EMBEDDINGS.transform(document))

class Embeddings(object):
    """
    Model that builds sentence embeddings from a list of tokens.

    Optional scoring method can be created to weigh tokens when creating embeddings. Averaging used if no scoring method provided.

    The model also applies principal component analysis using a LSA model. This reduces the noise of common but less
    relevant terms.
    """

    # pylint: disable = W0231
    def __init__(self, config=None):
        """
        Creates a new Embeddings model.

        Args:
            config: embeddings configuration
        """

        # Configuration
        self.config = config

        # Embeddings model
        self.embeddings = None
        self.lsa = None

        # Embedding scoring method - weighs each word in a sentence
        self.scoring = None

        # Word vector model
        self.vectors = self.loadVectors(self.config["path"]) if self.config else None

    def loadVectors(self, path):
        """
        Loads a word vector model at path.

        Args:
            path: path to word vector model

        Returns:
            Magnitude vector model
        """

        # Require that vector path exists, if a path is provided and it's not found, Magnitude will try download from it's servers
        if not path or not os.path.isfile(path):
            raise IOError(ENOENT, "Vector model file not found", path)

        # Load magnitude model. If this is a training run (no embeddings yet), block until the vectors are fully loaded
        return Magnitude(path, case_insensitive=True, blocking=True if not self.embeddings else False)

    def score(self, documents):
        """
        Builds a scoring index. Documents are tuples of (id, tokens, tags).

        Args:
            documents: array of documents
        """

        if self.config["scoring"]:
            # Create scoring object
            self.scoring = Scoring.create(self.config["scoring"])

            # Build scoring index over documents
            self.scoring.index(documents)

    def index(self, documents):
        """
        Builds an embeddings index. Documents are tuples of (id, tokens, tags).

        Args:
            documents: list of documents
        """

        ids = []
        embeddings = []
        stream = None

        # Shared objects with Pool
        args = (self.config, self.scoring)

        # Convert all documents to embedding arrays, stream embeddings to disk to control memory usage
        with Pool(os.cpu_count(), initializer=create, initargs=args) as pool:
            with tempfile.NamedTemporaryFile(mode="wb", suffix=".npy", delete=False) as output:
                stream = output.name
                for uid, embedding in pool.imap(transform, documents):
                    ids.append(uid)
                    pickle.dump(embedding, output)

        # Load streamed embeddings
        with open(stream, "rb") as stream:
            while True:
                try:
                    embeddings.append(pickle.load(stream))
                except EOFError:
                    break

        # Convert embeddings into a numpy array
        embeddings = np.array(embeddings)

        # Build LSA model (if enabled). Remove principal components from embeddings.
        self.lsa = self.buildLSA(embeddings, self.config["pca"]) if self.config["pca"] else None
        embeddings = self.removePC(embeddings) if self.lsa else embeddings

        # Normalize embeddings
        embeddings = self.normalize(embeddings)

        # Create embeddings index. Inner product is equal to cosine similarity on normalized vectors.
        # pylint: disable=E1136
        self.embeddings = faiss.index_factory(embeddings.shape[1], "IVF100,SQ8", faiss.METRIC_INNER_PRODUCT)

        # Train on embeddings model
        self.embeddings.train(embeddings)
        self.embeddings.add_with_ids(embeddings, np.array(ids))

    def buildLSA(self, embeddings, components):
        """
        Builds a LSA model. This model is used to remove the principal component within embeddings. This helps to
        smooth out noisy embeddings (common words with less value).

        Args:
            embeddings: input embeddings matrix
            components: number of model components

        Returns:
            LSA model
        """

        svd = TruncatedSVD(n_components=components, random_state=0)
        svd.fit(embeddings)

        return svd

    def removePC(self, embeddings):
        """
        Applies a LSA model to embeddings, removed the top n principal components.

        Args:
            embeddings: input embeddings matrix

        Returns:
            embeddings with the principal component(s) removed
        """

        pc = self.lsa.components_

        # Calculation is different if n_components = 1
        if pc.shape[0] == 1:
            return embeddings - embeddings.dot(pc.transpose()) * pc

        # Apply LSA model
        return embeddings - embeddings.dot(pc.transpose()).dot(pc)

    def normalize(self, embeddings):
        """
        Normalizes embeddings using L2 normalization.

        Args:
            embeddings: input embeddings matrix

        Returns:
            normalized embeddings
        """

        # Calculation is different for matrices vs vectors
        if len(embeddings.shape) > 1:
            return embeddings / np.linalg.norm(embeddings, axis=1).reshape(-1, 1)

        return embeddings / np.linalg.norm(embeddings)

    def transform(self, document):
        """
        Transforms document into an embeddings vector.

        Args:
            document: (id, tokens, tags)

        Returns:
            embeddings vector
        """

        # Generate weights for each vector using a scoring method
        weights = self.scoring.weights(document) if self.scoring else None

        # pylint: disable=E1133
        if weights and [x for x in weights if x > 0]:
            # Build weighted average embeddings vector. Create weights array os float32 to match embeddings precision.
            embedding = np.average(self.lookup(document[1]), weights=np.array(weights, dtype=np.float32), axis=0)
        else:
            # If no weights, use mean
            embedding = np.mean(self.lookup(document[1]), axis=0)

        # Reduce the dimensionality of the embeddings. Scale the embeddings using this
        # model to reduce the noise of common but less relevant terms.
        embedding = self.removePC(embedding) if self.lsa else embedding

        # Normalize vector if embeddings index exists, normalization is skipped during index builds
        return self.normalize(embedding) if self.embeddings else embedding

    def lookup(self, tokens):
        """
        Queries word vectors for given list of input tokens.

        Args:
            tokens: list of tokens to query

        Returns:
            word vectors array
        """

        return self.vectors.query(tokens)

    def search(self, tokens, limit=3):
        """
        Finds documents in the vector model most similar to the input document.

        Args:
            tokens: input tokens
            limit: maximum results

        Returns:
            list of topn matched (id, score)
        """

        # Convert tokens to embedding vector
        embedding = self.transform((None, tokens, None))

        # Search embeddings index
        self.embeddings.nprobe = 6
        results = self.embeddings.search(embedding.reshape(1, -1), limit)

        # Map results to [(id, score)]
        return list(zip(results[1][0].tolist(), (results[0][0]).tolist()))

    def similarity(self, query, documents):
        """
        Computes the similarity between a query and a set of documents

        Args:
            query: query tokens
            documents: document tokens

        Returns:
            [computed similarity (0 - 1 with 1 being most similar)]
        """

        query = self.transform((None, query, None)).reshape(1, -1)
        documents = np.array([self.transform((None, tokens, None)) for tokens in documents])

        # Dot product on normalized vectors is equal to cosine similarity
        return np.dot(query, documents.T)[0]

    def load(self, path):
        """
        Loads a pre-trained model.

        Models have the following files:
            config - configuration
            embeddings - sentence embeddings index
            lsa - LSA model, used to remove the principal component(s)
            scoring - scoring model used to weigh word vectors
            vectors - word vectors model

        Args:
            path: input directory path
        """

        with open("%s/config" % path, "rb") as handle:
            self.config = pickle.load(handle)

        # Sentence embeddings index
        self.embeddings = faiss.read_index("%s/embeddings" % path)

        with open("%s/lsa" % path, "rb") as handle:
            self.lsa = pickle.load(handle)

        # Embedding scoring
        if self.config["scoring"]:
            self.scoring = Scoring.create(self.config["scoring"])
            self.scoring.load(path)

        # Word embeddings
        self.vectors = self.loadVectors(self.config["path"])

    def save(self, path):
        """
        Saves a model.

        Args:
            path: output directory path
        """

        if self.config:
            with open("%s/config" % path, "wb") as handle:
                pickle.dump(self.config, handle, protocol=pickle.HIGHEST_PROTOCOL)

            # Write sentence embeddings
            faiss.write_index(self.embeddings, "%s/embeddings" % path)

            with open("%s/lsa" % path, "wb") as handle:
                pickle.dump(self.lsa, handle, protocol=pickle.HIGHEST_PROTOCOL)

            # Save embedding scoring
            if self.scoring:
                self.scoring.save(path)
