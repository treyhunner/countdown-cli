Contributor Guide
=================

How to report a bug
-------------------

Report bugs on the `Issue Tracker`_.

When filing an issue, make sure to answer these questions:

- Which operating system and Python version are you using?
- Which version of this project are you using?
- What did you do?
- What did you expect to see?
- What did you see instead?

The best way to get your bug fixed is to provide a test case,
and/or steps to reproduce the issue.

.. _Issue Tracker: https://github.com/treyhunner/countdown-cli/issues


How to request a feature
------------------------

Request features on the `Issue Tracker`_.


How to set up your development environment
------------------------------------------

You need Python, uv_, and just_ installed locally.
Nox_ is optional but required for the multi-version test matrix.

The CLI is exposed through the ``countdown`` script.
Run it directly from the synced environment:

.. code:: console

   uv run countdown 6m30s

.. _uv: https://docs.astral.sh/uv/
.. _just: https://github.com/casey/just
.. _Nox: https://nox.thea.codes/


How to test the project
-----------------------

This project uses pytest_ and Ruff_ orchestrated through ``just`` tasks.
Before opening a pull request, run the aggregated check:

.. code:: console

   just check

Useful individual commands:

.. code:: console

   just test -- -k timer
   just test-cov            # pytest with coverage (fail_under=100)

Unit tests are located in the ``tests`` directory,
and are written using the pytest_ testing framework.
Open ``htmlcov/index.html`` after ``just test-cov`` to debug coverage issues.

If you need to validate across every supported Python version, run:

.. code:: console

   just test-all

.. _pytest: https://pytest.readthedocs.io/
.. _Ruff: https://docs.astral.sh/ruff/
