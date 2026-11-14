import contextlib
import re
import zipfile

from click.testing import CliRunner
from intellireading.client.commands import (
    metaguide_epub_cmd,
    metaguide_xhtml_cmd,
    metaguide_dir_cmd,
)
from intellireading.client.metaguiding import _ABOUT_PAGE_FILENAME, _METAGUIDED_FLAG_FILENAME
import os


def test_metaguide_epub_cmd(tmp_path):
    runner = CliRunner()

    # get the epub test file path from the tests folder
    epub_test_file = os.path.join(os.path.dirname(__file__), "test_files", "input.epub")

    with contextlib.chdir(tmp_path):
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
            assert f"EPUB/{_ABOUT_PAGE_FILENAME}" in zip_ref.namelist()


def test_metaguide_epub_cmd_with_no_about_page(tmp_path):
    runner = CliRunner()

    epub_test_file = os.path.join(os.path.dirname(__file__), "test_files", "input.epub")

    with contextlib.chdir(tmp_path):
        result = runner.invoke(
            metaguide_epub_cmd,
            [
                "--input_file",
                epub_test_file,
                "--output_file",
                "output.epub",
                "--no_about_page",
            ],
        )

        assert result.exit_code == 0
        assert os.path.exists("output.epub")

        import zipfile

        with zipfile.ZipFile("output.epub", "r") as zip_ref:
            assert f"EPUB/{_ABOUT_PAGE_FILENAME}" not in zip_ref.namelist()
            assert _METAGUIDED_FLAG_FILENAME in zip_ref.namelist()


def test_metaguide_epub_cmd_with_remove_flag(tmp_path):
    runner = CliRunner()

    # get the epub test file path from the tests folder
    epub_test_file = os.path.join(os.path.dirname(__file__), "test_files", "input.epub")

    with contextlib.chdir(tmp_path):
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


def test_metaguide_xhtml_cmd(tmp_path):
    runner = CliRunner()

    # get the epub test file path from the tests folder
    xhtml_test_file = os.path.join(os.path.dirname(__file__), "test_files", "input.xhtml")

    with contextlib.chdir(tmp_path):
        # Run the command
        result = runner.invoke(metaguide_xhtml_cmd, ["--input_file", xhtml_test_file, "--output_file", "output.xhtml"])

        # Check the output
        assert result.exit_code == 0

        # Check that the output file was created
        assert os.path.exists("output.xhtml")


def test_metaguide_xhtml_cmd_with_remove_flag(tmp_path):
    runner = CliRunner()

    # get the epub test file path from the tests folder
    xhtml_test_file = os.path.join(os.path.dirname(__file__), "test_files", "input.xhtml")

    with contextlib.chdir(tmp_path):
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


def test_metaguide_dir_cmd(tmp_path):
    runner = CliRunner()

    # get the epub test file path from the tests folder
    test_dir = os.path.join(os.path.dirname(__file__), "test_files")

    with contextlib.chdir(tmp_path):
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
            assert f"EPUB/{_ABOUT_PAGE_FILENAME}" in zip_ref.namelist()


def test_metaguide_dir_cmd_with_no_about_page(tmp_path):
    runner = CliRunner()

    test_dir = os.path.join(os.path.dirname(__file__), "test_files")

    with contextlib.chdir(tmp_path):
        result = runner.invoke(
            metaguide_dir_cmd,
            ["--input_dir", test_dir, "--output_dir", "output", "--no_about_page"],
        )

        assert result.exit_code == 0
        assert os.path.exists("output/input.epub")

        import zipfile

        with zipfile.ZipFile("output/input.epub", "r") as zip_ref:
            assert f"EPUB/{_ABOUT_PAGE_FILENAME}" not in zip_ref.namelist()
            assert _METAGUIDED_FLAG_FILENAME in zip_ref.namelist()


def test_metaguide_dir_cmd_with_remove_flag(tmp_path):
    runner = CliRunner()

    # get the epub test file path from the tests folder
    test_dir = os.path.join(os.path.dirname(__file__), "test_files")

    with contextlib.chdir(tmp_path):
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


_SAMPLE_XHTML = b"""<?xml version="1.0" encoding="utf-8"?>
<html xmlns="http://www.w3.org/1999/xhtml"><body><p>reading metaguiding</p></body></html>"""


def _write_sample_xhtml(filename: str) -> None:
    with open(filename, "wb") as output_file:
        output_file.write(_SAMPLE_XHTML)


def test_metaguide_xhtml_cmd_with_fixation_level(tmp_path):
    runner = CliRunner()

    with contextlib.chdir(tmp_path):
        _write_sample_xhtml("input.xhtml")

        result = runner.invoke(
            metaguide_xhtml_cmd,
            ["--input_file", "input.xhtml", "--output_file", "output.xhtml", "--fixation", "1"],
        )

        assert result.exit_code == 0

        with open("output.xhtml", encoding="utf-8") as output_file:
            output_content = output_file.read()

        assert "<b>rea</b>ding" in output_content
        assert "<b>meta</b>guiding" in output_content


def test_metaguide_xhtml_cmd_fixation_level_five_bolds_more(tmp_path):
    runner = CliRunner()

    with contextlib.chdir(tmp_path):
        _write_sample_xhtml("input.xhtml")

        result = runner.invoke(
            metaguide_xhtml_cmd,
            ["--input_file", "input.xhtml", "--output_file", "output.xhtml", "--fixation", "5"],
        )

        assert result.exit_code == 0

        with open("output.xhtml", encoding="utf-8") as output_file:
            output_content = output_file.read()

        assert "<b>readi</b>ng" in output_content
        assert "<b>metaguid</b>ing" in output_content


def test_metaguide_xhtml_cmd_default_fixation_matches_level_three(tmp_path):
    runner = CliRunner()

    with contextlib.chdir(tmp_path):
        _write_sample_xhtml("input.xhtml")

        default_result = runner.invoke(
            metaguide_xhtml_cmd,
            ["--input_file", "input.xhtml", "--output_file", "default.xhtml"],
        )
        explicit_result = runner.invoke(
            metaguide_xhtml_cmd,
            ["--input_file", "input.xhtml", "--output_file", "explicit.xhtml", "--fixation", "3"],
        )

        assert default_result.exit_code == 0
        assert explicit_result.exit_code == 0

        with open("default.xhtml", "rb") as default_file:
            default_content = default_file.read()
        with open("explicit.xhtml", "rb") as explicit_file:
            explicit_content = explicit_file.read()

        assert default_content == explicit_content


def test_metaguide_xhtml_cmd_rejects_invalid_fixation_level(tmp_path):
    runner = CliRunner()

    with contextlib.chdir(tmp_path):
        _write_sample_xhtml("input.xhtml")

        result = runner.invoke(
            metaguide_xhtml_cmd,
            ["--input_file", "input.xhtml", "--output_file", "output.xhtml", "--fixation", "6"],
        )

        assert result.exit_code != 0
        assert not os.path.exists("output.xhtml")


_CHAPTER_PATH = "EPUB/xhtml/basic_tests.xhtml"


def _chapter_bold_length_sum(epub_path: str) -> int:
    with zipfile.ZipFile(epub_path) as zip_file:
        content = zip_file.read(_CHAPTER_PATH).decode("utf-8")

    return sum(len(bold) for bold in re.findall(r"<b>(.*?)</b>", content, re.DOTALL))


def test_metaguide_epub_cmd_with_fixation_level(tmp_path):
    runner = CliRunner()

    epub_test_file = os.path.join(os.path.dirname(__file__), "test_files", "input.epub")

    with contextlib.chdir(tmp_path):
        level_1_result = runner.invoke(
            metaguide_epub_cmd,
            ["--input_file", epub_test_file, "--output_file", "level_1.epub", "--fixation", "1"],
        )
        level_5_result = runner.invoke(
            metaguide_epub_cmd,
            ["--input_file", epub_test_file, "--output_file", "level_5.epub", "--fixation", "5"],
        )

        assert level_1_result.exit_code == 0
        assert level_5_result.exit_code == 0
        assert _chapter_bold_length_sum("level_1.epub") < _chapter_bold_length_sum("level_5.epub")


def test_metaguide_dir_cmd_with_fixation_level(tmp_path):
    runner = CliRunner()

    test_dir = os.path.join(os.path.dirname(__file__), "test_files")

    with contextlib.chdir(tmp_path):
        level_one_result = runner.invoke(
            metaguide_dir_cmd,
            ["--input_dir", test_dir, "--output_dir", "output_level_1", "--fixation", "1"],
        )
        level_five_result = runner.invoke(
            metaguide_dir_cmd,
            ["--input_dir", test_dir, "--output_dir", "output_level_5", "--fixation", "5"],
        )

        assert level_one_result.exit_code == 0
        assert level_five_result.exit_code == 0

        with open("output_level_1/input.xhtml", encoding="utf-8") as level_one_file:
            level_one_content = level_one_file.read()
        with open("output_level_5/input.xhtml", encoding="utf-8") as level_five_file:
            level_five_content = level_five_file.read()

        assert "<b>" in level_one_content
        assert "<b>" in level_five_content
        assert level_one_content != level_five_content
