# Employee Contract Allowances

Employee allowances management from contract.

## Usage

- Create new Allowance (example Retail) with code ALL-R
- Add this Allowance to employee contract and specify amount
- Add this Allowance to your salary structure with :
  - condition : `result = allowances.ALL-R and allowances.ALL-R.amount or False`
  - value : `result = allowances.ALL-R.amount`

## Bug Tracker

Bugs are tracked on [Gitlab Issues](https://gitlab.com/hadooc/odoo/payroll/issues).

## Maintainer

![Hadooc](https://hadooc.com/logo)

This module is maintained by Hadooc.

To contribute to this module, please visit [Contributing Page](https://gitlab.com/hadooc/extra/wikis/Contributing).
