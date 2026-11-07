"""Doxygen validates real parameter/return docs, including with version 1.9.8."""
import xml.etree.ElementTree as ET

import pytest

from test_graph_bfs_documentation import run_doxygen


def test_documented_parameters_and_return_are_parsed_in_both_outputs(tmp_path):
    source = tmp_path / 'documented.c'
    source.write_text('''/** @file documented.c */
/**
 * @brief Return the supplied integer.
 * @param value Integer to return unchanged.
 * @return The supplied value.
 */
int identity(int value) { return value; }
''', encoding='utf-8')
    run_doxygen(tmp_path, [source])
    assert (tmp_path / 'doxygen/html/index.html').is_file()
    tree = ET.parse(tmp_path / 'doxygen/xml/documented_8c.xml')
    member = tree.find('.//memberdef[name="identity"]')
    assert member is not None
    assert member.findtext('.//parametername') == 'value'
    assert member.find('.//simplesect[@kind="return"]/para') is not None


@pytest.mark.parametrize('documentation', [
    '/** @brief Return an integer, with required parameter and return docs absent. */',
    '/** @brief Return an integer.\n * @param wrong_name Unknown parameter.\n * @return The value.\n */',
])
def test_missing_or_invalid_parameter_docs_still_fail(tmp_path, documentation):
    source = tmp_path / 'undocumented.c'
    source.write_text('/** @file undocumented.c */\n' + documentation +
                      '\nint identity(int value) { return value; }\n', encoding='utf-8')
    with pytest.raises(AssertionError):
        run_doxygen(tmp_path, [source])
    assert 'warning:' in (tmp_path / 'warnings.log').read_text(encoding='utf-8')
