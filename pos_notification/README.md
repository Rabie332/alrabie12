# POS Notification

This module provides a simple toast notification.

**Table of contents**

- [Overview](#overview)
- [Configuration](#configuration)
- [Bug Tracker](#bug-tracker)
- [Maintainer](#maintainer)

## Overview

This module provides a simple toast notification.

Here is an example of usage:

```javascript
const {notification_utils} = require("pos_notification.notification_utils");
class HelloWorld extends PosComponent {
  async onClick() {
    notification_utils.showNotification(this, `Hello world.`, 3000);
  }
}
```

## Configuration

## Bug Tracker

Bugs are tracked on Bugs are tracked on
[Gitlab Issues](https://gitlab.com/hadooc/odoo/pos/-/issues)

In case of trouble, please check there if your issue has already been reported. If you
spotted it first, help us smash it by providing detailed and welcomed feedback.

## Maintainer

![Hadooc](https://hadooc.com/logo)

This module is maintained by Hadooc.

To contribute to this module, please visit
[Contributing Page](https://gitlab.com/hadooc/extra/wikis/Contributing).
