"""
Report factory module
"""

import os.path

from .annotate import Annotate
from .csvr import CSV
from .markdown import Markdown
from .task import Task

from ..models import Models


class Execute:
    """
    Creates a Report
    """

    @staticmethod
    def create(render, embeddings, db, options):
        """
        Factory method to construct a Report.

        Args:
            render: report rendering format
            embeddings: embeddings index
            db: database connection
            options: report options

        Returns:
            Report
        """

        if render == "ant":
            return Annotate(embeddings, db, options)
        if render == "csv":
            return CSV(embeddings, db, options)
        if render == "md":
            return Markdown(embeddings, db, options)

        raise ValueError(f"Invalid report format: {render}")

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
        name, options, queries, outdir = Task.load(task)

        # Override report options with any command line options
        options = Execute.options(options, topn, render, path, qa, indir, threshold)

        # Derive report format
        render = options["render"] if options["render"] else "md"

        # Create report object. Default to Markdown.
        report = Execute.create(render, embeddings, db, options)

        # Generate output filename
        outfile = os.path.join(outdir, f"{name}.{render}")

        # Stream report to file
        with open(outfile, "w", encoding="utf-8") as output:
            # Build the report
            report.build(queries, options, output)

        # Free any resources
        report.cleanup(outfile)

        # Free resources
        Models.close(db)

    @staticmethod
    def options(options, topn, render, path, qa, indir, threshold):
        """
        Combine report and command line options with command line options taking precedence.

        Args:
            options: report options
            topn: number of results
            render: report rendering format ("md" for markdown, "csv" for csv, "ant" for pdf annotation)
            path: embeddings model path
            qa: qa model path
            indir: path to input directory containing source files
            threshold: query match score threshold

        Returns:
            combined options
        """

        options["topn"] = topn if topn is not None else options.get("topn")
        options["render"] = render if render else options.get("render")
        options["path"] = path if path else options.get("path")
        options["qa"] = qa if qa else options.get("qa")
        options["indir"] = indir if indir else options.get("indir")
        options["threshold"] = threshold if threshold is not None else options.get("threshold")

        return options
