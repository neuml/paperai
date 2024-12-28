"""
Highlights module
"""

import itertools

import networkx

from txtai.pipeline import Tokenizer


class Highlights:
    """
    Methods to extract highlights from a list of text sections.
    """

    # Domain specific stop list
    STOP_WORDS = {
        "abstract",
        "al",
        "article",
        "arxiv",
        "author",
        "biorxiv",
        "copyright",
        "da",
        "dei",
        "del",
        "dell",
        "della",
        "delle",
        "di",
        "doi",
        "et",
        "fig",
        "figure",
        "funder",
        "holder",
        "http",
        "https",
        "il",
        "la",
        "le",
        "license",
        "medrxiv",
        "non",
        "org",
        "peer",
        "peer-reviewed",
        "permission",
        "preprint",
        "publication",
        "pubmed",
        "reserved",
        "reviewed",
        "rights",
        "si",
        "una",
        "used",
        "using",
    }

    @staticmethod
    def build(sections, topn):
        """
        Extracts highlights from a list of sections. This method uses textrank to find sections with the highest
        importance across the input list. This method attempts to return important but unique results to limit
        repetitive statements.

        Args:
            sections: input sections
            topn: top n results to return

        Results:
            top n sections
        """

        results = []

        # Rank the text using textrank for importance within collection
        for uid, _ in Highlights.textrank(sections):
            # Lookup text and tokenize
            text = [text for u, text in sections if u == uid][0]
            tokens = Highlights.tokenize(text)

            # Compare text to existing results, look for highly unique results
            # This finds results that are important but not repetitive
            unique = all(Highlights.jaccardIndex(t, tokens) <= 0.2 for _, t in results)
            if unique:
                results.append((uid, tokens))

        uids = [uid for uid, _ in results][:topn]

        # Get related text for each match
        return [text for uid, text in sections if uid in uids]

    @staticmethod
    def textrank(sections):
        """
        Runs the textrank algorithm against the list of sections. Orders the list into descending order of importance
        given the list.

        Args:
            sections: list of sentences

        Returns:
            sorted list using the textrank algorithm
        """

        # Build the graph network
        graph = Highlights.buildGraph(sections)

        # Run pagerank
        rank = networkx.pagerank(graph, weight="weight")

        # Return items sorted by highest score first
        return sorted(list(rank.items()), key=lambda x: x[1], reverse=True)

    @staticmethod
    def buildGraph(nodes):
        """
        Builds a graph of nodes using input.

        Args:
            nodes: input graph nodes

        Returns:
            graph
        """

        graph = networkx.Graph()
        graph.add_nodes_from([uid for (uid, _) in nodes])

        # Tokenize nodes, store uid and tokens
        vectors = []
        for uid, text in nodes:
            # Custom tokenization that works best with textrank matching
            tokens = Highlights.tokenize(text)

            if len(tokens) >= 3:
                vectors.append((uid, tokens))

        pairs = list(itertools.combinations(vectors, 2))

        # add edges to the graph
        for pair in pairs:
            node1, tokens1 = pair[0]
            node2, tokens2 = pair[1]

            # Add a graph edge and compute the cosine similarity for the weight
            graph.add_edge(node1, node2, weight=Highlights.jaccardIndex(tokens1, tokens2))

        return graph

    @staticmethod
    def jaccardIndex(set1, set2):
        """
        Jaccard index calculation used for similarity.

        Args:
            set1: input 1
            set2: input 2

        Returns:
            jaccard index
        """

        n = len(set1.intersection(set2))
        return n / float(len(set1) + len(set2) - n) if n > 0 else 0

    @staticmethod
    def tokenize(text):
        """
        Tokenizes text into tokens, removes domain specific stop words.

        Args:
            text: input text

        Returns:
            tokens
        """

        # Remove additional stop words to improve highlighting results
        return {token for token in Tokenizer.tokenize(text) if token not in Highlights.STOP_WORDS}
