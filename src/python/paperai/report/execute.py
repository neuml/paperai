"""
Report factory module
"""

import os.path

from .annotate import Annotate
from .csvr import CSV
from .markdown import Markdown
from .task import Task

from ..models import Models

class Execute(object):
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
    def run(task, topn=None, render=None, path=None, qa=None, indir=None):
        """
        Reads a list of queries from a task file and builds a report.

        Args:
            task: input task file
            topn: number of results
            render: report rendering format ("md" for markdown, "csv" for csv, "ant" for pdf annotation)
            path: embeddings model path
            qa: qa model path
            indir: path to input directory containing source files
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
            report.build(queries, topn, output)

        # Free any resources
        report.cleanup(outfile)

        # Free resources
        Models.close(db)
