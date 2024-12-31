# HR Payroll Period

Adds the concept of period in the human resources management.

The objective of the module is to create periods of time to be used in the human resources management flows such as
specific payroll period of time or timesheet periods.

Regarding to payrolls, it adds the date of payment on the payslip and payslip batch. This date is automatically filled
when selecting a period. It also adds a sequence on the payslip batch name and the company on the payslip batch.

**Table of contents**

- [Installation](#installation)
- [Configuration](#configuration)
  - [Create a fiscal year](#Create-fiscale-year)
- [Usage](#usage)
  - [Create a payslip batch](#create-payslip-batch)
- [Known issues / Roadmap](#known-issues-roadmap)

- [Bug Tracker](#bug-tracker)
- [Maintainer](#maintainer)

## Installation

Install the payroll of your localization, then install this module.

## Configuration

#### Create a fiscal year

Go to: Human Resources -> Configuration -> Payroll -> Payroll Fiscal Year

- Select a type of schedule, e.g. monthly
- Select a duration, e.g. from 2020-01-01 to 2020-12-31
- Select when the payment is done, e.g. the second day of the next period
- Click on create periods, then confirm

The first period of the year is now open and ready to be used.

Some companies have employees paid at different types of schedule. In that case, you need to create as many fiscal years
as types of schedule required. The same applies in a multi-company configuration.

## Usage

#### Create a payslip batch

Go to: Human Resources -> Payroll -> Payslip Batches

The first period of the fiscal year is already selected. You may change it if you manage multiple types of schedules.

- Click on Generate Payslips

The employees paid with the selected schedule are automatically selected.

- Click on Generate

- Confirm your payslips

- Click on Close

The payroll period is closed automatically and the next one is open.

## Known issues / Roadmap

- Currently it is not possible to close the HR fiscal year before the end of the end of the last period. When
  implementing this feature, contracts and opened payslips should be updated with the new period assigned.
- It is not possible to use the date_range module in server tools to generate semi-monthly periods so those periods are
  generated as in previous versions.
- The date_range module does not allow to create a period for just one day.

## Bug Tracker

Bugs are tracked on [Gitlab Issues](https://gitlab.com/hadooc/odoo/payroll/issues)

In case of trouble, please check there if your issue has already been reported. If you spotted it first, help us smash
it by providing detailed and welcomed feedback.

## Maintainer

![Hadooc](https://hadooc.com/logo)

This module is maintained by Hadooc.

To contribute to this module, please visit [Contributing Page](https://gitlab.com/hadooc/extra/wikis/Contributing).
