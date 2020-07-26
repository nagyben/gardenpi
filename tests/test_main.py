import main
import unittest.mock as mock


@mock.patch("main.main_loop")
def test_main(main_loop):
    main.main()

    main_loop.assert_called_once()
