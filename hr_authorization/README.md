# HR Authorization

This module allows you to request an authorization to the administration service.

You have some type of authorization sache as: Personal affair, Work mission, etc...

The request authorization passed by some stages: Draft -> First approve -> Second approve -> (Done / Refused)

Then, the user can print the authorization.

**Table of contents**

- [Overview](#overview)
  - [Create new authorization](#create-new-authorization)
  - [Approve](#first-approve)
- [Configuration](#configuration)
  - [Adding authorization stages](#adding-authorization-stages)
  - [Adding authorization types](#adding-authorization-types)
- [Bug Tracker](#bug-tracker)
- [Maintainer](#maintainer)

## Overview

#### Create new authorization

Go to Employees -> Authorizations -> Create

![Create Auth](static/description/create_auth.png)

#### Approve

Go to Employees -> Authorizations , then the user can 'Accept' or 'Refuse' the authorization to the next approve.

![Approve](static/description/first_approve.png)

## Configuration

#### Adding authorization stages

You need to configure the default user for each stage to accept the authorization: Go to Employees -> Authorizations ->
Configuration -> Authorization Stages -> Select "First approve" -> Edit -> Default user
![Config Stages](static/description/config_stage.png)

#### Adding authorization types

Also you need to configure authorization type: Go to Employees -> Authorizations -> Configuration -> Authorization Types
![Config Types](static/description/config_type.png)

## Bug Tracker

Bugs are tracked on [Gitlab Issues](https://gitlab.com/hadooc/odoo/hr/-/issues)

In case of trouble, please check there if your issue has already been reported. If you spotted it first, help us smash
it by providing detailed and welcomed feedback.

## Maintainer

![Hadooc](https://hadooc.com/logo)

This module is maintained by Hadooc.

To contribute to this module, please visit [Contributing Page](https://gitlab.com/hadooc/extra/wikis/Contributing).
