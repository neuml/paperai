"""
Report factory module
"""

import os.path

from .annotate import Annotate
from .csvr import CSV
from .markdown import Markdown
from .task import Task
from abc import ABCMeta, abstractstaticmethod

from ..models import Models

class IExecute(metaclass=ABCMeta):

    @abstractstaticmethod
    def create(render, embeddings, db, qa, indir):
        pass

    @abstractstaticmethod
    def run(task, topn=None, render=None, path=None, qa=None, indir=None, threshold=None):
        pass



class Execute(IExecute):

    __instance = None

    @staticmethod
    def get_instance():
        if Execute.__instance == None:
            Execute("expected", 0)
        return __instance

    def __init__(self, embeddings, render):
        if Execute.__instance != None:
            raise Exception("Cannot be instatiated more than once")
        else:
        self.embeddings = embeddings
        self.render = render
        Execute.__instance = self

    """
    Creates a Report
    """

    @staticmethod
    def create(render, embeddings, db, qa, indir):
        """
        Factory method to construct a Report.

        Args:
            render: report rendering format
            embeddings: embeddings index
            db: database connection
            qa: qa model path
            indir: path to input directory containing source files

        Returns:
            Report
        """

        if render == "ant":
            return Annotate(embeddings, db, qa, indir)
        elif render == "csv":
            return CSV(embeddings, db, qa)
        elif render == "md":
            return Markdown(embeddings, db, qa)

        return None

    @staticmethod
    def run(task, topn=None, render=None, path=None, qa=None, indir=None, threshold=None):
        """
        Reads a list of queries from a task file and builds a report.

        Args:
            task: input task file
            topn: number of results
            render: report rendering format ("md" for markdown, "csv" for csv, "ant" for pdf annotation)
            path: embeddings model path
            qa: qa model path
            indir: path to input directory containing source files
            threshold: query match score threshold
        """

        # Load model
        embeddings, db = Models.load(path)

        # Read task configuration
        name, queries, outdir = Task.load(task)

        # Derive report format
        render = render if render else "md"

        # Create report object. Default to Markdown.
        report = Execute.create(render, embeddings, db, qa, indir)

        # Generate output filename
        outfile = os.path.join(outdir, "%s.%s" % (name, render))

        # Stream report to file
        with open(outfile, "w") as output:
            # Build the report
            report.build(queries, topn, threshold, output)

        # Free any resources
        report.cleanup(outfile)

        # Free resources
        Models.close(db)
