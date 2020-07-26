import unittest.mock as mock
import mcp


class MockMCP:
    def read_adc(self, channel: int):
        return channel


@mock.patch("mcp.MCP", new_callable=MockMCP)
def test_readmcp(mock_mcp):
    actual = mcp.readmcp(0)
    expected = 0
    assert actual == expected

    actual = mcp.readmcp(1)
    expected = 1
    assert actual == expected
