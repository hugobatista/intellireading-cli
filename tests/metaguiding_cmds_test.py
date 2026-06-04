from click.testing import CliRunner
from intellireading.client.commands import (
    metaguide_epub_cmd,
    metaguide_xhtml_cmd,
    metaguide_dir_cmd,
)
from intellireading.client.metaguiding import _METAGUIDED_FLAG_FILENAME
import os


def test_metaguide_epub_cmd():
    runner = CliRunner()

    # get the epub test file path from the tests folder
    epub_test_file = os.path.join(os.path.dirname(__file__), "test_files", "input.epub")

    with runner.isolated_filesystem():
        # Run the command
        result = runner.invoke(metaguide_epub_cmd, ["--input_file", epub_test_file, "--output_file", "output.epub"])

        # Check the output
        assert result.exit_code == 0

        # Check that the output file was created
        assert os.path.exists("output.epub")

        # open the output zip file and check that the metaguide flag file was created
        import zipfile

        with zipfile.ZipFile("output.epub", "r") as zip_ref:
            zip_ref.extractall("output")
            flag_file_path = f"output/{_METAGUIDED_FLAG_FILENAME}"
            assert os.path.exists(flag_file_path)


def test_metaguide_epub_cmd_with_remove_flag():
    runner = CliRunner()

    # get the epub test file path from the tests folder
    epub_test_file = os.path.join(os.path.dirname(__file__), "test_files", "input.epub")

    with runner.isolated_filesystem():
        # metaguide the epub file first
        # Run the command
        result = runner.invoke(metaguide_epub_cmd, ["--input_file", epub_test_file, "--output_file", "metaguided.epub"])

        # Check the output
        assert result.exit_code == 0

        # Check that the metaguided file was created
        assert os.path.exists("metaguided.epub")

        # run the command again to remove the metaguiding
        result = runner.invoke(
            metaguide_epub_cmd,
            ["--input_file", "metaguided.epub", "--output_file", "output.epub", "--remove_metaguiding"],
        )

        # Check the output
        assert result.exit_code == 0
        # Check that the output file was created
        assert os.path.exists("output.epub")

        import zipfile

        with zipfile.ZipFile("output.epub", "r") as zip_ref:
            zip_ref.extractall("output")
            # open the output zip file and check that the metaguide flag file was removed
            flag_file_path = f"output/{_METAGUIDED_FLAG_FILENAME}"
            assert not os.path.exists(flag_file_path)

            # iterate all xhtml or html files in the output folder and check for bold tags
            for file in zip_ref.namelist():
                if file.endswith(".xhtml") or file.endswith(".html"):
                    with zip_ref.open(file) as xhtml_file:
                        xhtml_content = xhtml_file.read().decode("utf-8")
                        assert "<b>" not in xhtml_content


def test_metaguide_xhtml_cmd():
    runner = CliRunner()

    # get the epub test file path from the tests folder
    xhtml_test_file = os.path.join(os.path.dirname(__file__), "test_files", "input.xhtml")

    with runner.isolated_filesystem():
        # Run the command
        result = runner.invoke(metaguide_xhtml_cmd, ["--input_file", xhtml_test_file, "--output_file", "output.xhtml"])

        # Check the output
        assert result.exit_code == 0

        # Check that the output file was created
        assert os.path.exists("output.xhtml")


def test_metaguide_xhtml_cmd_with_remove_flag():
    runner = CliRunner()

    # get the epub test file path from the tests folder
    xhtml_test_file = os.path.join(os.path.dirname(__file__), "test_files", "input.xhtml")

    with runner.isolated_filesystem():
        # metaguide the xhtml file first
        result = runner.invoke(
            metaguide_xhtml_cmd, ["--input_file", xhtml_test_file, "--output_file", "metaguided.xhtml"]
        )

        # Check the output
        assert result.exit_code == 0

        # Check that the metaguided file was created
        assert os.path.exists("metaguided.xhtml")

        # ensure we have a <b> tag in the input file
        with open("metaguided.xhtml", encoding="utf-8") as file:
            assert "<b>" in file.read()

        # Run the command
        result = runner.invoke(
            metaguide_xhtml_cmd,
            ["--input_file", "metaguided.xhtml", "--output_file", "output.xhtml", "--remove_metaguiding"],
        )

        # Check the output
        assert result.exit_code == 0

        # Check that the output file was created
        assert os.path.exists("output.xhtml")

        with open("output.xhtml", encoding="utf-8") as output_file:
            output_content = output_file.read()

            # checks if there is any <b> tag in the output file
            assert "<b>" not in output_content


def test_metaguide_dir_cmd():
    runner = CliRunner()

    # get the epub test file path from the tests folder
    test_dir = os.path.join(os.path.dirname(__file__), "test_files")

    with runner.isolated_filesystem():
        # Run the command
        result = runner.invoke(metaguide_dir_cmd, ["--input_dir", test_dir, "--output_dir", "output"])

        # Check the output
        assert result.exit_code == 0

        # Check that the output file was created
        assert os.path.exists("output/input.epub")
        assert os.path.exists("output/input.xhtml")

        # open the output zip file and check that the metaguide flag file was created
        import zipfile

        with zipfile.ZipFile("output/input.epub", "r") as zip_ref:
            zip_ref.extractall("output")
            flag_file_path = f"output/{_METAGUIDED_FLAG_FILENAME}"
            assert os.path.exists(flag_file_path)


def test_metaguide_dir_cmd_with_remove_flag():
    runner = CliRunner()

    # get the epub test file path from the tests folder
    test_dir = os.path.join(os.path.dirname(__file__), "test_files")

    with runner.isolated_filesystem():
        # metaguide the directory first
        result = runner.invoke(metaguide_dir_cmd, ["--input_dir", test_dir, "--output_dir", "metaguided_output"])

        # Check the output
        assert result.exit_code == 0

        # Run the command
        result = runner.invoke(
            metaguide_dir_cmd, ["--input_dir", "metaguided_output", "--output_dir", "output", "--remove_metaguiding"]
        )

        # Check the output
        assert result.exit_code == 0

        # Check that the output file was created
        assert os.path.exists("output/input.epub")
        assert os.path.exists("output/input.xhtml")

        import zipfile

        with zipfile.ZipFile("output/input.epub", "r") as zip_ref:
            zip_ref.extractall("output")
            # open the output zip file and check that the metaguide flag file was removed
            flag_file_path = f"output/{_METAGUIDED_FLAG_FILENAME}"
            assert not os.path.exists(flag_file_path)

            # iterate all xhtml or html files in the output folder and check for bold tags
            for file in zip_ref.namelist():
                if file.endswith(".xhtml") or file.endswith(".html"):
                    with zip_ref.open(file) as xhtml_file:
                        xhtml_content = xhtml_file.read().decode("utf-8")
                        assert "<b>" not in xhtml_content

        with open("output/input.xhtml", encoding="utf-8") as output_file:
            output_content = output_file.read()

            # checks if there is any <b> tag in the output file
            assert "<b>" not in output_content
