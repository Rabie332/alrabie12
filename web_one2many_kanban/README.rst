==================================
Web One2many Kanban
==================================

alt: License: AGPL-3

Description
-----------

* This module extends functionality of kanban view.
* Display one2many record in kanban view.
* Display One2many records in kanban view.
* You need to define o2m field in kanban view definition and use for loop(same way we use in qweb) to display fields in kanban view.
* This module is developed to extend the functionality of kanban view.
* It fills the gap at certain extent by allowing to display one2many records in kanban view.

You need to define one2many field in kanban view definition and use
for loop to display fields like:

`<t t-foreach="record.one2manyfield.raw_value" t-as="o">`

`	<t t-esc="o.name">`

`	<t t-esc="o.many2onefield[1]">`

`</t>`


Bug Tracker
===========

Credits
=======

Contributors
------------

* Serpent Consulting Services Pvt. Ltd. <support@serpentcs.com>
