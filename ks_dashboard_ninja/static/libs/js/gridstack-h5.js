/* ! For license information please see gridstack-h5.js.LICENSE.txt */
!(function (t, e) {
    typeof exports === "object" && typeof module === "object"
        ? (module.exports = e())
        : typeof define === "function" && define.amd
        ? define([], e)
        : typeof exports === "object"
        ? (exports.GridStack = e())
        : (t.GridStack = e());
})(self, function () {
    return (() => {
        "use strict";
        var t = {
                21: (t, e, i) => {
                    Object.defineProperty(e, "__esModule", { value: !0 }),
                        (e.GridStackDD = void 0);
                    const s = i(334),
                        o = i(270),
                        r = i(593);
                    class n extends s.GridStackDDI {
                        static get() {
                            return s.GridStackDDI.get();
                        }
                        remove(t) {
                            return (
                                this.draggable(t, "destroy").resizable(
                                    t,
                                    "destroy"
                                ),
                                t.gridstackNode &&
                                    delete t.gridstackNode._initDD,
                                this
                            );
                        }
                    }
                    function l(t, e) {
                        const i = t ? t.gridstackNode : void 0;
                        i &&
                            i.grid &&
                            (e
                                ? (i._isAboutToRemove = !0)
                                : delete i._isAboutToRemove,
                            e
                                ? t.classList.add("grid-stack-item-removing")
                                : t.classList.remove(
                                      "grid-stack-item-removing"
                                  ));
                    }
                    (e.GridStackDD = n),
                        (o.GridStack.prototype._setupAcceptWidget =
                            function () {
                                if (
                                    this.opts.staticGrid ||
                                    (!this.opts.acceptWidgets &&
                                        !this.opts.removable)
                                )
                                    return (
                                        n.get().droppable(this.el, "destroy"),
                                        this
                                    );
                                let t,
                                    e,
                                    i,
                                    s = (s, o, l) => {
                                        const a = o.gridstackNode;
                                        if (!a) return;
                                        const h = (l =
                                                l || o).getBoundingClientRect(),
                                            d = h.left - t.left,
                                            g = h.top - t.top,
                                            p = {
                                                position: { top: g, left: d },
                                            };
                                        if (a._temporaryRemoved) {
                                            if (
                                                ((a.x = Math.max(
                                                    0,
                                                    Math.round(d / i)
                                                )),
                                                (a.y = Math.max(
                                                    0,
                                                    Math.round(g / e)
                                                )),
                                                delete a.autoPosition,
                                                this.engine.nodeBoundFix(a),
                                                !this.engine.willItFit(a))
                                            ) {
                                                if (
                                                    ((a.autoPosition = !0),
                                                    !this.engine.willItFit(a))
                                                )
                                                    return void n
                                                        .get()
                                                        .off(o, "drag");
                                                a._willFitPos &&
                                                    (r.Utils.copyPos(
                                                        a,
                                                        a._willFitPos
                                                    ),
                                                    delete a._willFitPos);
                                            }
                                            this._onStartMoving(
                                                l,
                                                s,
                                                p,
                                                a,
                                                i,
                                                e
                                            );
                                        } else
                                            this._dragOrResize(
                                                l,
                                                s,
                                                p,
                                                a,
                                                i,
                                                e
                                            );
                                    };
                                return (
                                    n
                                        .get()
                                        .droppable(this.el, {
                                            accept: (t) => {
                                                const e = t.gridstackNode;
                                                if (
                                                    (e == null
                                                        ? void 0
                                                        : e.grid) === this
                                                )
                                                    return !0;
                                                if (!this.opts.acceptWidgets)
                                                    return !1;
                                                let i = !0;
                                                if (
                                                    typeof this.opts
                                                        .acceptWidgets ===
                                                    "function"
                                                )
                                                    i =
                                                        this.opts.acceptWidgets(
                                                            t
                                                        );
                                                else {
                                                    const e =
                                                        !0 ===
                                                        this.opts.acceptWidgets
                                                            ? ".grid-stack-item"
                                                            : this.opts
                                                                  .acceptWidgets;
                                                    i = t.matches(e);
                                                }
                                                if (
                                                    i &&
                                                    e &&
                                                    this.opts.maxRow
                                                ) {
                                                    const t = {
                                                        w: e.w,
                                                        h: e.h,
                                                        minW: e.minW,
                                                        minH: e.minH,
                                                    };
                                                    i =
                                                        this.engine.willItFit(
                                                            t
                                                        );
                                                }
                                                return i;
                                            },
                                        })
                                        .on(this.el, "dropover", (o, r, a) => {
                                            let h = r.gridstackNode;
                                            if (
                                                (h == null
                                                    ? void 0
                                                    : h.grid) === this &&
                                                !h._temporaryRemoved
                                            )
                                                return !1;
                                            (h == null ? void 0 : h.grid) &&
                                                h.grid !== this &&
                                                !h._temporaryRemoved &&
                                                h.grid._leave(r, a);
                                            const d =
                                                this.el.getBoundingClientRect();
                                            (t = { top: d.top, left: d.left }),
                                                (i = this.cellWidth()),
                                                (e = this.getCellHeight(!0)),
                                                h || (h = this._readAttr(r)),
                                                h.grid ||
                                                    ((h._isExternal = !0),
                                                    (r.gridstackNode = h)),
                                                (a = a || r);
                                            const g =
                                                    h.w ||
                                                    Math.round(
                                                        a.offsetWidth / i
                                                    ) ||
                                                    1,
                                                p =
                                                    h.h ||
                                                    Math.round(
                                                        a.offsetHeight / e
                                                    ) ||
                                                    1;
                                            return (
                                                h.grid && h.grid !== this
                                                    ? (r._gridstackNodeOrig ||
                                                          (r._gridstackNodeOrig =
                                                              h),
                                                      (r.gridstackNode = h =
                                                          Object.assign(
                                                              Object.assign(
                                                                  {},
                                                                  h
                                                              ),
                                                              {
                                                                  w: g,
                                                                  h: p,
                                                                  grid: this,
                                                              }
                                                          )),
                                                      this.engine
                                                          .cleanupNode(h)
                                                          .nodeBoundFix(h),
                                                      (h._initDD =
                                                          h._isExternal =
                                                          h._temporaryRemoved =
                                                              !0))
                                                    : ((h.w = g),
                                                      (h.h = p),
                                                      (h._temporaryRemoved =
                                                          !0)),
                                                l(h.el, !1),
                                                n.get().on(r, "drag", s),
                                                s(o, r, a),
                                                !1
                                            );
                                        })
                                        .on(this.el, "dropout", (t, e, i) => {
                                            const s = e.gridstackNode;
                                            return (
                                                Boolean(s) &&
                                                ((s.grid && s.grid !== this) ||
                                                    this._leave(e, i),
                                                !1)
                                            );
                                        })
                                        .on(this.el, "drop", (t, e, i) => {
                                            const s = e.gridstackNode;
                                            if (
                                                (s == null
                                                    ? void 0
                                                    : s.grid) === this &&
                                                !s._isExternal
                                            )
                                                return !1;
                                            const o = Boolean(
                                                this.placeholder.parentElement
                                            );
                                            this.placeholder.remove();
                                            const l = e._gridstackNodeOrig;
                                            if (
                                                (delete e._gridstackNodeOrig,
                                                o &&
                                                    l &&
                                                    l.grid &&
                                                    l.grid !== this)
                                            ) {
                                                const t = l.grid;
                                                t.engine.removedNodes.push(l),
                                                    t._triggerRemoveEvent();
                                            }
                                            return (
                                                Boolean(s) &&
                                                (o &&
                                                    (this.engine.cleanupNode(s),
                                                    (s.grid = this)),
                                                n.get().off(e, "drag"),
                                                i !== e
                                                    ? (i.remove(),
                                                      (e.gridstackNode = l),
                                                      o &&
                                                          (e = e.cloneNode(!0)))
                                                    : (e.remove(),
                                                      n.get().remove(e)),
                                                Boolean(o) &&
                                                    ((e.gridstackNode = s),
                                                    (s.el = e),
                                                    r.Utils.copyPos(
                                                        s,
                                                        this._readAttr(
                                                            this.placeholder
                                                        )
                                                    ),
                                                    r.Utils.removePositioningStyles(
                                                        e
                                                    ),
                                                    this._writeAttr(e, s),
                                                    this.el.appendChild(e),
                                                    this._updateContainerHeight(),
                                                    this.engine.addedNodes.push(
                                                        s
                                                    ),
                                                    this._triggerAddEvent(),
                                                    this._triggerChangeEvent(),
                                                    this.engine.endUpdate(),
                                                    this._gsEventHandler
                                                        .dropped &&
                                                        this._gsEventHandler.dropped(
                                                            Object.assign(
                                                                Object.assign(
                                                                    {},
                                                                    t
                                                                ),
                                                                {
                                                                    type: "dropped",
                                                                }
                                                            ),
                                                            l && l.grid
                                                                ? l
                                                                : void 0,
                                                            s
                                                        ),
                                                    window.setTimeout(() => {
                                                        s.el &&
                                                        s.el.parentElement
                                                            ? this._prepareDragDropByNode(
                                                                  s
                                                              )
                                                            : this.engine.removeNode(
                                                                  s
                                                              );
                                                    }),
                                                    !1))
                                            );
                                        }),
                                    this
                                );
                            }),
                        (o.GridStack.prototype._setupRemoveDrop = function () {
                            if (
                                !this.opts.staticGrid &&
                                typeof this.opts.removable === "string"
                            ) {
                                const t = document.querySelector(
                                    this.opts.removable
                                );
                                if (!t) return this;
                                n.get().isDroppable(t) ||
                                    n
                                        .get()
                                        .droppable(
                                            t,
                                            this.opts.removableOptions
                                        )
                                        .on(t, "dropover", (t, e) => l(e, !0))
                                        .on(t, "dropout", (t, e) => l(e, !1));
                            }
                            return this;
                        }),
                        (o.GridStack.setupDragIn = function (t, e) {
                            let i, s;
                            if (
                                (t &&
                                    ((i = t),
                                    (s = Object.assign(
                                        Object.assign(
                                            {},
                                            {
                                                revert: "invalid",
                                                handle: ".grid-stack-item-content",
                                                scroll: !1,
                                                appendTo: "body",
                                            }
                                        ),
                                        e || {}
                                    ))),
                                typeof i !== "string")
                            )
                                return;
                            const o = n.get();
                            r.Utils.getElements(i).forEach((t) => {
                                o.isDraggable(t) || o.dragIn(t, s);
                            });
                        }),
                        (o.GridStack.prototype._prepareDragDropByNode =
                            function (t) {
                                const e = t.el,
                                    i = n.get();
                                if (
                                    this.opts.staticGrid ||
                                    ((t.noMove || this.opts.disableDrag) &&
                                        (t.noResize || this.opts.disableResize))
                                )
                                    return (
                                        t._initDD &&
                                            (i.remove(e), delete t._initDD),
                                        e.classList.add(
                                            "ui-draggable-disabled",
                                            "ui-resizable-disabled"
                                        ),
                                        this
                                    );
                                if (!t._initDD) {
                                    let s,
                                        o,
                                        n = (i, r) => {
                                            this._gsEventHandler[i.type] &&
                                                this._gsEventHandler[i.type](
                                                    i,
                                                    i.target
                                                ),
                                                (s = this.cellWidth()),
                                                (o = this.getCellHeight(!0)),
                                                this._onStartMoving(
                                                    e,
                                                    i,
                                                    r,
                                                    t,
                                                    s,
                                                    o
                                                );
                                        },
                                        l = (i, r) => {
                                            this._dragOrResize(
                                                e,
                                                i,
                                                r,
                                                t,
                                                s,
                                                o
                                            );
                                        },
                                        a = (s) => {
                                            this.placeholder.remove(),
                                                delete t._moving,
                                                delete t._lastTried;
                                            const o = s.target;
                                            if (
                                                o.gridstackNode &&
                                                o.gridstackNode.grid === this
                                            ) {
                                                if (
                                                    ((t.el = o),
                                                    t._isAboutToRemove)
                                                ) {
                                                    const r =
                                                        e.gridstackNode.grid;
                                                    r._gsEventHandler[s.type] &&
                                                        r._gsEventHandler[
                                                            s.type
                                                        ](s, o),
                                                        i.remove(e),
                                                        r.engine.removedNodes.push(
                                                            t
                                                        ),
                                                        r._triggerRemoveEvent(),
                                                        delete e.gridstackNode,
                                                        delete t.el,
                                                        e.remove();
                                                } else
                                                    t._temporaryRemoved
                                                        ? (r.Utils.removePositioningStyles(
                                                              o
                                                          ),
                                                          r.Utils.copyPos(
                                                              t,
                                                              t._orig
                                                          ),
                                                          this._writePosAttr(
                                                              o,
                                                              t
                                                          ),
                                                          this.engine.addNode(
                                                              t
                                                          ))
                                                        : (r.Utils.removePositioningStyles(
                                                              o
                                                          ),
                                                          this._writePosAttr(
                                                              o,
                                                              t
                                                          )),
                                                        this._gsEventHandler[
                                                            s.type
                                                        ] &&
                                                            this._gsEventHandler[
                                                                s.type
                                                            ](s, o);
                                                (this._extraDragRow = 0),
                                                    this._updateContainerHeight(),
                                                    this._triggerChangeEvent(),
                                                    this.engine.endUpdate();
                                            }
                                        };
                                    i
                                        .draggable(e, {
                                            start: n,
                                            stop: a,
                                            drag: l,
                                        })
                                        .resizable(e, {
                                            start: n,
                                            stop: a,
                                            resize: l,
                                        }),
                                        (t._initDD = !0);
                                }
                                return (
                                    t.noMove || this.opts.disableDrag
                                        ? (i.draggable(e, "disable"),
                                          e.classList.add(
                                              "ui-draggable-disabled"
                                          ))
                                        : (i.draggable(e, "enable"),
                                          e.classList.remove(
                                              "ui-draggable-disabled"
                                          )),
                                    t.noResize || this.opts.disableResize
                                        ? (i.resizable(e, "disable"),
                                          e.classList.add(
                                              "ui-resizable-disabled"
                                          ))
                                        : (i.resizable(e, "enable"),
                                          e.classList.remove(
                                              "ui-resizable-disabled"
                                          )),
                                    this
                                );
                            }),
                        (o.GridStack.prototype._onStartMoving = function (
                            t,
                            e,
                            i,
                            s,
                            o,
                            r
                        ) {
                            if (
                                (this.engine.cleanNodes().beginUpdate(s),
                                this._writePosAttr(this.placeholder, s),
                                this.el.appendChild(this.placeholder),
                                (s.el = this.placeholder),
                                (s._lastUiPosition = i.position),
                                (s._prevYPix = i.position.top),
                                (s._moving = e.type === "dragstart"),
                                delete s._lastTried,
                                e.type === "dropover" &&
                                    s._temporaryRemoved &&
                                    (this.engine.addNode(s), (s._moving = !0)),
                                this.engine.cacheRects(
                                    o,
                                    r,
                                    this.opts.marginTop,
                                    this.opts.marginRight,
                                    this.opts.marginBottom,
                                    this.opts.marginLeft
                                ),
                                e.type === "resizestart")
                            ) {
                                const e = n
                                    .get()
                                    .resizable(
                                        t,
                                        "option",
                                        "minWidth",
                                        o * (s.minW || 1)
                                    )
                                    .resizable(
                                        t,
                                        "option",
                                        "minHeight",
                                        r * (s.minH || 1)
                                    );
                                s.maxW &&
                                    e.resizable(
                                        t,
                                        "option",
                                        "maxWidth",
                                        o * s.maxW
                                    ),
                                    s.maxH &&
                                        e.resizable(
                                            t,
                                            "option",
                                            "maxHeight",
                                            r * s.maxH
                                        );
                            }
                        }),
                        (o.GridStack.prototype._leave = function (t, e) {
                            const i = t.gridstackNode;
                            i &&
                                (n.get().off(t, "drag"),
                                i._temporaryRemoved ||
                                    ((i._temporaryRemoved = !0),
                                    this.engine.removeNode(i),
                                    (i.el = i._isExternal && e ? e : t),
                                    !0 === this.opts.removable && l(t, !0),
                                    t._gridstackNodeOrig
                                        ? ((t.gridstackNode =
                                              t._gridstackNodeOrig),
                                          delete t._gridstackNodeOrig)
                                        : i._isExternal &&
                                          (delete i.el,
                                          delete t.gridstackNode,
                                          this.engine.restoreInitial())));
                        }),
                        (o.GridStack.prototype._dragOrResize = function (
                            t,
                            e,
                            i,
                            s,
                            o,
                            n
                        ) {
                            let l,
                                a = Object.assign({}, s._orig),
                                h = this.opts.marginLeft,
                                d = this.opts.marginRight,
                                g = this.opts.marginTop,
                                p = this.opts.marginBottom,
                                c = Math.round(0.1 * n),
                                u = Math.round(0.1 * o);
                            if (
                                ((h = Math.min(h, u)),
                                (d = Math.min(d, u)),
                                (g = Math.min(g, c)),
                                (p = Math.min(p, c)),
                                e.type === "drag")
                            ) {
                                if (s._temporaryRemoved) return;
                                const e = i.position.top - s._prevYPix;
                                (s._prevYPix = i.position.top),
                                    r.Utils.updateScrollPosition(
                                        t,
                                        i.position,
                                        e
                                    );
                                const l =
                                        i.position.left +
                                        (i.position.left >
                                        s._lastUiPosition.left
                                            ? -d
                                            : h),
                                    c =
                                        i.position.top +
                                        (i.position.top > s._lastUiPosition.top
                                            ? -p
                                            : g);
                                (a.x = Math.round(l / o)),
                                    (a.y = Math.round(c / n));
                                const u = this._extraDragRow;
                                if (this.engine.collide(s, a)) {
                                    let t = this.getRow(),
                                        e = Math.max(0, a.y + s.h - t);
                                    this.opts.maxRow &&
                                        t + e > this.opts.maxRow &&
                                        (e = Math.max(0, this.opts.maxRow - t)),
                                        (this._extraDragRow = e);
                                } else this._extraDragRow = 0;
                                if (
                                    (this._extraDragRow !== u &&
                                        this._updateContainerHeight(),
                                    s.x === a.x && s.y === a.y)
                                )
                                    return;
                            } else if (e.type === "resize") {
                                if (a.x < 0) return;
                                if (
                                    (r.Utils.updateScrollResize(e, t, n),
                                    (a.w = Math.round((i.size.width - h) / o)),
                                    (a.h = Math.round((i.size.height - g) / n)),
                                    s.w === a.w && s.h === a.h)
                                )
                                    return;
                                if (
                                    s._lastTried &&
                                    s._lastTried.w === a.w &&
                                    s._lastTried.h === a.h
                                )
                                    return;
                                const d = i.position.left + h,
                                    p = i.position.top + g;
                                (a.x = Math.round(d / o)),
                                    (a.y = Math.round(p / n)),
                                    (l = !0);
                            }
                            s._lastTried = a;
                            const m = {
                                x: i.position.left + h,
                                y: i.position.top + g,
                                w: (i.size ? i.size.width : s.w * o) - h - d,
                                h: (i.size ? i.size.height : s.h * n) - g - p,
                            };
                            if (
                                this.engine.moveNodeCheck(
                                    s,
                                    Object.assign(Object.assign({}, a), {
                                        cellWidth: o,
                                        cellHeight: n,
                                        rect: m,
                                        resizing: l,
                                    })
                                )
                            ) {
                                (s._lastUiPosition = i.position),
                                    this.engine.cacheRects(o, n, g, d, p, h),
                                    delete s._skipDown,
                                    l &&
                                        s.subGrid &&
                                        s.subGrid.onParentResize(),
                                    (this._extraDragRow = 0),
                                    this._updateContainerHeight();
                                const t = e.target;
                                this._writePosAttr(t, s),
                                    this._gsEventHandler[e.type] &&
                                        this._gsEventHandler[e.type](e, t);
                            }
                        }),
                        (o.GridStack.prototype.movable = function (t, e) {
                            return (
                                this.opts.staticGrid ||
                                    o.GridStack.getElements(t).forEach((t) => {
                                        const i = t.gridstackNode;
                                        i &&
                                            (e
                                                ? delete i.noMove
                                                : (i.noMove = !0),
                                            this._prepareDragDropByNode(i));
                                    }),
                                this
                            );
                        }),
                        (o.GridStack.prototype.resizable = function (t, e) {
                            return (
                                this.opts.staticGrid ||
                                    o.GridStack.getElements(t).forEach((t) => {
                                        const i = t.gridstackNode;
                                        i &&
                                            (e
                                                ? delete i.noResize
                                                : (i.noResize = !0),
                                            this._prepareDragDropByNode(i));
                                    }),
                                this
                            );
                        }),
                        (o.GridStack.prototype.disable = function () {
                            if (!this.opts.staticGrid)
                                return (
                                    this.enableMove(!1),
                                    this.enableResize(!1),
                                    this._triggerEvent("disable"),
                                    this
                                );
                        }),
                        (o.GridStack.prototype.enable = function () {
                            if (!this.opts.staticGrid)
                                return (
                                    this.enableMove(!0),
                                    this.enableResize(!0),
                                    this._triggerEvent("enable"),
                                    this
                                );
                        }),
                        (o.GridStack.prototype.enableMove = function (t) {
                            return (
                                this.opts.staticGrid ||
                                    ((this.opts.disableDrag = !t),
                                    this.engine.nodes.forEach((e) =>
                                        this.movable(e.el, t)
                                    )),
                                this
                            );
                        }),
                        (o.GridStack.prototype.enableResize = function (t) {
                            return (
                                this.opts.staticGrid ||
                                    ((this.opts.disableResize = !t),
                                    this.engine.nodes.forEach((e) =>
                                        this.resizable(e.el, t)
                                    )),
                                this
                            );
                        });
                },
                334: (t, e) => {
                    Object.defineProperty(e, "__esModule", { value: !0 }),
                        (e.GridStackDDI = void 0);
                    class i {
                        static registerPlugin(t) {
                            return (i.ddi = new t()), i.ddi;
                        }
                        static get() {
                            return i.ddi || i.registerPlugin(i);
                        }
                        remove(t) {
                            return this;
                        }
                    }
                    e.GridStackDDI = i;
                },
                62: (t, e, i) => {
                    Object.defineProperty(e, "__esModule", { value: !0 }),
                        (e.GridStackEngine = void 0);
                    const s = i(593);
                    class o {
                        constructor(t = {}) {
                            (this.addedNodes = []),
                                (this.removedNodes = []),
                                (this.column = t.column || 12),
                                (this.onChange = t.onChange),
                                (this._float = t.float),
                                (this.maxRow = t.maxRow),
                                (this.nodes = t.nodes || []);
                        }
                        batchUpdate() {
                            return (
                                this.batchMode ||
                                    ((this.batchMode = !0),
                                    (this._prevFloat = this._float),
                                    (this._float = !0),
                                    this.saveInitial()),
                                this
                            );
                        }
                        commit() {
                            return this.batchMode
                                ? ((this.batchMode = !1),
                                  (this._float = this._prevFloat),
                                  delete this._prevFloat,
                                  this._packNodes()._notify())
                                : this;
                        }
                        _useEntireRowArea(t, e) {
                            return (
                                !this.float &&
                                !this._hasLocked &&
                                (!t._moving || t._skipDown || e.y <= t.y)
                            );
                        }
                        _fixCollisions(t, e = t, i, o = {}) {
                            if (
                                (this._sortNodes(-1),
                                !(i = i || this.collide(t, e)))
                            )
                                return !1;
                            if (
                                t._moving &&
                                !o.nested &&
                                !this.float &&
                                this.swap(t, i)
                            )
                                return !0;
                            let r = e;
                            this._useEntireRowArea(t, e) &&
                                ((r = { x: 0, w: this.column, y: e.y, h: e.h }),
                                (i = this.collide(t, r, o.skip)));
                            let n = !1,
                                l = { nested: !0, pack: !1 };
                            for (; (i = i || this.collide(t, r, o.skip)); ) {
                                let r;
                                if (
                                    (i.locked ||
                                    (t._moving &&
                                        !t._skipDown &&
                                        e.y > t.y &&
                                        !this.float &&
                                        (!this.collide(
                                            i,
                                            Object.assign(
                                                Object.assign({}, i),
                                                { y: t.y }
                                            ),
                                            t
                                        ) ||
                                            !this.collide(
                                                i,
                                                Object.assign(
                                                    Object.assign({}, i),
                                                    { y: e.y - i.h }
                                                ),
                                                t
                                            )))
                                        ? ((t._skipDown =
                                              t._skipDown || e.y > t.y),
                                          (r = this.moveNode(
                                              t,
                                              Object.assign(
                                                  Object.assign(
                                                      Object.assign({}, e),
                                                      { y: i.y + i.h }
                                                  ),
                                                  l
                                              )
                                          )),
                                          i.locked && r
                                              ? s.Utils.copyPos(e, t)
                                              : !i.locked &&
                                                r &&
                                                o.pack &&
                                                (this._packNodes(),
                                                (e.y = i.y + i.h),
                                                s.Utils.copyPos(t, e)),
                                          (n = n || r))
                                        : (r = this.moveNode(
                                              i,
                                              Object.assign(
                                                  Object.assign(
                                                      Object.assign({}, i),
                                                      { y: e.y + e.h, skip: t }
                                                  ),
                                                  l
                                              )
                                          )),
                                    !r)
                                )
                                    return n;
                                i = void 0;
                            }
                            return n;
                        }
                        collide(t, e = t, i) {
                            return this.nodes.find(
                                (o) =>
                                    o !== t &&
                                    o !== i &&
                                    s.Utils.isIntercepted(o, e)
                            );
                        }
                        collideAll(t, e = t, i) {
                            return this.nodes.filter(
                                (o) =>
                                    o !== t &&
                                    o !== i &&
                                    s.Utils.isIntercepted(o, e)
                            );
                        }
                        collideCoverage(t, e, i) {
                            if (!e.rect || !t._rect) return;
                            let s,
                                o = t._rect,
                                r = Object.assign({}, e.rect);
                            return (
                                r.y > o.y
                                    ? ((r.h += r.y - o.y), (r.y = o.y))
                                    : (r.h += o.y - r.y),
                                r.x > o.x
                                    ? ((r.w += r.x - o.x), (r.x = o.x))
                                    : (r.w += o.x - r.x),
                                i.forEach((t) => {
                                    if (t.locked || !t._rect) return;
                                    let e = t._rect,
                                        i = Number.MAX_VALUE,
                                        n = Number.MAX_VALUE,
                                        l = 0.5;
                                    o.y < e.y
                                        ? (i = (r.y + r.h - e.y) / e.h)
                                        : o.y + o.h > e.y + e.h &&
                                          (i = (e.y + e.h - r.y) / e.h),
                                        o.x < e.x
                                            ? (n = (r.x + r.w - e.x) / e.w)
                                            : o.x + o.w > e.x + e.w &&
                                              (n = (e.x + e.w - r.x) / e.w);
                                    const a = Math.min(n, i);
                                    a > l && ((l = a), (s = t));
                                }),
                                s
                            );
                        }
                        cacheRects(t, e, i, s, o, r) {
                            return (
                                this.nodes.forEach(
                                    (n) =>
                                        (n._rect = {
                                            y: n.y * e + i,
                                            x: n.x * t + r,
                                            w: n.w * t - r - s,
                                            h: n.h * e - i - o,
                                        })
                                ),
                                this
                            );
                        }
                        swap(t, e) {
                            if (!e || e.locked || !t || t.locked) return !1;
                            function i() {
                                const i = e.x,
                                    s = e.y;
                                return (
                                    (e.x = t.x),
                                    (e.y = t.y),
                                    t.h != e.h
                                        ? ((t.x = i), (t.y = e.y + e.h))
                                        : t.w != e.w
                                        ? ((t.x = e.x + e.w), (t.y = s))
                                        : ((t.x = i), (t.y = s)),
                                    (t._dirty = e._dirty = !0),
                                    !0
                                );
                            }
                            let o;
                            if (
                                t.w === e.w &&
                                t.h === e.h &&
                                (t.x === e.x || t.y === e.y) &&
                                (o = s.Utils.isTouching(t, e))
                            )
                                return i();
                            if (!1 !== o) {
                                if (
                                    t.w === e.w &&
                                    t.x === e.x &&
                                    (o || (o = s.Utils.isTouching(t, e)))
                                ) {
                                    if (e.y < t.y) {
                                        const i = t;
                                        (t = e), (e = i);
                                    }
                                    return i();
                                }
                                if (!1 !== o) {
                                    if (
                                        t.h === e.h &&
                                        t.y === e.y &&
                                        (o || (o = s.Utils.isTouching(t, e)))
                                    ) {
                                        if (e.x < t.x) {
                                            const i = t;
                                            (t = e), (e = i);
                                        }
                                        return i();
                                    }
                                    return !1;
                                }
                            }
                        }
                        isAreaEmpty(t, e, i, s) {
                            const o = {
                                x: t || 0,
                                y: e || 0,
                                w: i || 1,
                                h: s || 1,
                            };
                            return !this.collide(o);
                        }
                        compact() {
                            if (this.nodes.length === 0) return this;
                            this.batchUpdate()._sortNodes();
                            const t = this.nodes;
                            return (
                                (this.nodes = []),
                                t.forEach((t) => {
                                    t.locked || (t.autoPosition = !0),
                                        this.addNode(t, !1),
                                        (t._dirty = !0);
                                }),
                                this.commit()
                            );
                        }
                        set float(t) {
                            this._float !== t &&
                                ((this._float = t || !1),
                                t || this._packNodes()._notify());
                        }
                        get float() {
                            return this._float || !1;
                        }
                        _sortNodes(t) {
                            return (
                                (this.nodes = s.Utils.sort(
                                    this.nodes,
                                    t,
                                    this.column
                                )),
                                this
                            );
                        }
                        _packNodes() {
                            return (
                                this.batchMode ||
                                    (this._sortNodes(),
                                    this.float
                                        ? this.nodes.forEach((t) => {
                                              if (
                                                  t._updating ||
                                                  void 0 === t._orig ||
                                                  t.y === t._orig.y
                                              )
                                                  return;
                                              let e = t.y;
                                              for (; e > t._orig.y; )
                                                  --e,
                                                      this.collide(t, {
                                                          x: t.x,
                                                          y: e,
                                                          w: t.w,
                                                          h: t.h,
                                                      }) ||
                                                          ((t._dirty = !0),
                                                          (t.y = e));
                                          })
                                        : this.nodes.forEach((t, e) => {
                                              if (!t.locked)
                                                  for (; t.y > 0; ) {
                                                      const i =
                                                          e === 0 ? 0 : t.y - 1;
                                                      if (
                                                          e !== 0 &&
                                                          this.collide(t, {
                                                              x: t.x,
                                                              y: i,
                                                              w: t.w,
                                                              h: t.h,
                                                          })
                                                      )
                                                          break;
                                                      (t._dirty = t.y !== i),
                                                          (t.y = i);
                                                  }
                                          })),
                                this
                            );
                        }
                        prepareNode(t, e) {
                            ((t = t || {})._id = t._id || o._idSeq++),
                                (void 0 !== t.x &&
                                    void 0 !== t.y &&
                                    t.x !== null &&
                                    t.y !== null) ||
                                    (t.autoPosition = !0);
                            const i = { x: 0, y: 0, w: 1, h: 1 };
                            return (
                                s.Utils.defaults(t, i),
                                t.autoPosition || delete t.autoPosition,
                                t.noResize || delete t.noResize,
                                t.noMove || delete t.noMove,
                                typeof t.x === "string" && (t.x = Number(t.x)),
                                typeof t.y === "string" && (t.y = Number(t.y)),
                                typeof t.w === "string" && (t.w = Number(t.w)),
                                typeof t.h === "string" && (t.h = Number(t.h)),
                                isNaN(t.x) &&
                                    ((t.x = i.x), (t.autoPosition = !0)),
                                isNaN(t.y) &&
                                    ((t.y = i.y), (t.autoPosition = !0)),
                                isNaN(t.w) && (t.w = i.w),
                                isNaN(t.h) && (t.h = i.h),
                                this.nodeBoundFix(t, e)
                            );
                        }
                        nodeBoundFix(t, e) {
                            const i = t._orig || s.Utils.copyPos({}, t);
                            return (
                                t.maxW && (t.w = Math.min(t.w, t.maxW)),
                                t.maxH && (t.h = Math.min(t.h, t.maxH)),
                                t.minW &&
                                    t.minW <= this.column &&
                                    (t.w = Math.max(t.w, t.minW)),
                                t.minH && (t.h = Math.max(t.h, t.minH)),
                                t.w > this.column
                                    ? (this.column < 12 &&
                                          !this._inColumnResize &&
                                          ((t.w = Math.min(12, t.w)),
                                          this.cacheOneLayout(t, 12)),
                                      (t.w = this.column))
                                    : t.w < 1 && (t.w = 1),
                                this.maxRow && t.h > this.maxRow
                                    ? (t.h = this.maxRow)
                                    : t.h < 1 && (t.h = 1),
                                t.x < 0 && (t.x = 0),
                                t.y < 0 && (t.y = 0),
                                t.x + t.w > this.column &&
                                    (e
                                        ? (t.w = this.column - t.x)
                                        : (t.x = this.column - t.w)),
                                this.maxRow &&
                                    t.y + t.h > this.maxRow &&
                                    (e
                                        ? (t.h = this.maxRow - t.y)
                                        : (t.y = this.maxRow - t.h)),
                                s.Utils.samePos(t, i) || (t._dirty = !0),
                                t
                            );
                        }
                        getDirtyNodes(t) {
                            return t
                                ? this.nodes.filter(
                                      (t) =>
                                          t._dirty &&
                                          !s.Utils.samePos(t, t._orig)
                                  )
                                : this.nodes.filter((t) => t._dirty);
                        }
                        _notify(t, e = !0) {
                            if (this.batchMode) return this;
                            const i = (t =
                                void 0 === t
                                    ? []
                                    : Array.isArray(t)
                                    ? t
                                    : [t]).concat(this.getDirtyNodes());
                            return this.onChange && this.onChange(i, e), this;
                        }
                        cleanNodes() {
                            return (
                                this.batchMode ||
                                    this.nodes.forEach((t) => {
                                        delete t._dirty, delete t._lastTried;
                                    }),
                                this
                            );
                        }
                        saveInitial() {
                            return (
                                this.nodes.forEach((t) => {
                                    (t._orig = s.Utils.copyPos({}, t)),
                                        delete t._dirty;
                                }),
                                (this._hasLocked = this.nodes.some(
                                    (t) => t.locked
                                )),
                                this
                            );
                        }
                        restoreInitial() {
                            return (
                                this.nodes.forEach((t) => {
                                    s.Utils.samePos(t, t._orig) ||
                                        (s.Utils.copyPos(t, t._orig),
                                        (t._dirty = !0));
                                }),
                                this._notify(),
                                this
                            );
                        }
                        addNode(t, e = !1) {
                            const i = this.nodes.find((e) => e._id === t._id);
                            if (i) return i;
                            if (
                                (delete (t = this._inColumnResize
                                    ? this.nodeBoundFix(t)
                                    : this.prepareNode(t))._temporaryRemoved,
                                delete t._removeDOM,
                                t.autoPosition)
                            ) {
                                this._sortNodes();
                                for (let e = 0; ; ++e) {
                                    const i = e % this.column,
                                        o = Math.floor(e / this.column);
                                    if (i + t.w > this.column) continue;
                                    const r = { x: i, y: o, w: t.w, h: t.h };
                                    if (
                                        !this.nodes.find((t) =>
                                            s.Utils.isIntercepted(r, t)
                                        )
                                    ) {
                                        (t.x = i),
                                            (t.y = o),
                                            delete t.autoPosition;
                                        break;
                                    }
                                }
                            }
                            return (
                                this.nodes.push(t),
                                e && this.addedNodes.push(t),
                                this._fixCollisions(t),
                                this.batchMode || this._packNodes()._notify(),
                                t
                            );
                        }
                        removeNode(t, e = !0, i = !1) {
                            return this.nodes.find((e) => e === t)
                                ? (i && this.removedNodes.push(t),
                                  e && (t._removeDOM = !0),
                                  (this.nodes = this.nodes.filter(
                                      (e) => e !== t
                                  )),
                                  this._packNodes()._notify(t))
                                : this;
                        }
                        removeAll(t = !0) {
                            return (
                                delete this._layouts,
                                this.nodes.length === 0
                                    ? this
                                    : (t &&
                                          this.nodes.forEach(
                                              (t) => (t._removeDOM = !0)
                                          ),
                                      (this.removedNodes = this.nodes),
                                      (this.nodes = []),
                                      this._notify(this.removedNodes))
                            );
                        }
                        moveNodeCheck(t, e) {
                            if (!this.changedPosConstrain(t, e)) return !1;
                            if (((e.pack = !0), !this.maxRow))
                                return this.moveNode(t, e);
                            let i,
                                r = new o({
                                    column: this.column,
                                    float: this.float,
                                    nodes: this.nodes.map((e) =>
                                        e === t
                                            ? ((i = Object.assign({}, e)), i)
                                            : Object.assign({}, e)
                                    ),
                                });
                            if (!i) return !1;
                            let n = r.moveNode(i, e);
                            if (
                                this.maxRow &&
                                n &&
                                ((n = r.getRow() <= this.maxRow),
                                !n && !e.resizing)
                            ) {
                                const i = this.collide(t, e);
                                if (i && this.swap(t, i))
                                    return this._notify(), !0;
                            }
                            return (
                                Boolean(n) &&
                                (r.nodes
                                    .filter((t) => t._dirty)
                                    .forEach((t) => {
                                        const e = this.nodes.find(
                                            (e) => e._id === t._id
                                        );
                                        e &&
                                            (s.Utils.copyPos(e, t),
                                            (e._dirty = !0));
                                    }),
                                this._notify(),
                                !0)
                            );
                        }
                        willItFit(t) {
                            if ((delete t._willFitPos, !this.maxRow)) return !0;
                            const e = new o({
                                    column: this.column,
                                    float: this.float,
                                    nodes: this.nodes.map((t) =>
                                        Object.assign({}, t)
                                    ),
                                }),
                                i = Object.assign({}, t);
                            return (
                                this.cleanupNode(i),
                                delete i.el,
                                delete i._id,
                                delete i.content,
                                delete i.grid,
                                e.addNode(i),
                                e.getRow() <= this.maxRow &&
                                    ((t._willFitPos = s.Utils.copyPos({}, i)),
                                    !0)
                            );
                        }
                        changedPosConstrain(t, e) {
                            return (
                                (e.w = e.w || t.w),
                                (e.h = e.h || t.h),
                                t.x !== e.x ||
                                    t.y !== e.y ||
                                    (t.maxW && (e.w = Math.min(e.w, t.maxW)),
                                    t.maxH && (e.h = Math.min(e.h, t.maxH)),
                                    t.minW && (e.w = Math.max(e.w, t.minW)),
                                    t.minH && (e.h = Math.max(e.h, t.minH)),
                                    t.w !== e.w || t.h !== e.h)
                            );
                        }
                        moveNode(t, e) {
                            if (!t || !e) return !1;
                            void 0 === e.pack && (e.pack = !0),
                                typeof e.x !== "number" && (e.x = t.x),
                                typeof e.y !== "number" && (e.y = t.y),
                                typeof e.w !== "number" && (e.w = t.w),
                                typeof e.h !== "number" && (e.h = t.h);
                            let i = t.w !== e.w || t.h !== e.h,
                                o = s.Utils.copyPos({}, t, !0);
                            if (
                                (s.Utils.copyPos(o, e),
                                (o = this.nodeBoundFix(o, i)),
                                s.Utils.copyPos(e, o),
                                s.Utils.samePos(t, e))
                            )
                                return !1;
                            let r = s.Utils.copyPos({}, t),
                                n = o,
                                l = this.collideAll(t, n, e.skip),
                                a = !0;
                            if (l.length) {
                                const i =
                                    t._moving && !e.nested
                                        ? this.collideCoverage(t, e, l)
                                        : l[0];
                                a =
                                    Boolean(i) &&
                                    !this._fixCollisions(t, o, i, e);
                            }
                            return (
                                a && ((t._dirty = !0), s.Utils.copyPos(t, o)),
                                e.pack && this._packNodes()._notify(),
                                !s.Utils.samePos(t, r)
                            );
                        }
                        getRow() {
                            return this.nodes.reduce(
                                (t, e) => Math.max(t, e.y + e.h),
                                0
                            );
                        }
                        beginUpdate(t) {
                            return (
                                t._updating ||
                                    ((t._updating = !0),
                                    delete t._skipDown,
                                    this.batchMode || this.saveInitial()),
                                this
                            );
                        }
                        endUpdate() {
                            const t = this.nodes.find((t) => t._updating);
                            return (
                                t && (delete t._updating, delete t._skipDown),
                                this
                            );
                        }
                        save(t = !0) {
                            var e;
                            const i =
                                    (e = this._layouts) === null || void 0 === e
                                        ? void 0
                                        : e.length,
                                s =
                                    i && this.column !== i - 1
                                        ? this._layouts[i - 1]
                                        : null,
                                o = [];
                            return (
                                this._sortNodes(),
                                this.nodes.forEach((e) => {
                                    const i =
                                            s == null
                                                ? void 0
                                                : s.find(
                                                      (t) => t._id === e._id
                                                  ),
                                        r = Object.assign({}, e);
                                    i &&
                                        ((r.x = i.x), (r.y = i.y), (r.w = i.w));
                                    for (const t in r)
                                        (t[0] !== "_" &&
                                            r[t] !== null &&
                                            void 0 !== r[t]) ||
                                            delete r[t];
                                    delete r.grid,
                                        t || delete r.el,
                                        r.autoPosition || delete r.autoPosition,
                                        r.noResize || delete r.noResize,
                                        r.noMove || delete r.noMove,
                                        r.locked || delete r.locked,
                                        o.push(r);
                                }),
                                o
                            );
                        }
                        layoutsNodesChange(t) {
                            return (
                                !this._layouts ||
                                    this._inColumnResize ||
                                    this._layouts.forEach((e, i) => {
                                        if (!e || i === this.column)
                                            return this;
                                        if (i < this.column)
                                            this._layouts[i] = void 0;
                                        else {
                                            const s = i / this.column;
                                            t.forEach((t) => {
                                                if (!t._orig) return;
                                                const i = e.find(
                                                    (e) => e._id === t._id
                                                );
                                                i &&
                                                    (t.y !== t._orig.y &&
                                                        (i.y +=
                                                            t.y - t._orig.y),
                                                    t.x !== t._orig.x &&
                                                        (i.x = Math.round(
                                                            t.x * s
                                                        )),
                                                    t.w !== t._orig.w &&
                                                        (i.w = Math.round(
                                                            t.w * s
                                                        )));
                                            });
                                        }
                                    }),
                                this
                            );
                        }
                        updateNodeWidths(t, e, i, o = "moveScale") {
                            var r;
                            if (!this.nodes.length || !e || t === e)
                                return this;
                            this.cacheLayout(this.nodes, t), this.batchUpdate();
                            let n = [],
                                l = !1;
                            if (e === 1 && (i == null ? void 0 : i.length)) {
                                l = !0;
                                let t = 0;
                                i.forEach((e) => {
                                    (e.x = 0),
                                        (e.w = 1),
                                        (e.y = Math.max(e.y, t)),
                                        (t = e.y + e.h);
                                }),
                                    (n = i),
                                    (i = []);
                            } else i = s.Utils.sort(this.nodes, -1, t);
                            let a = [];
                            if (e > t) {
                                a = this._layouts[e] || [];
                                const s = this._layouts.length - 1;
                                !a.length &&
                                    t !== s &&
                                    ((r = this._layouts[s]) === null ||
                                    void 0 === r
                                        ? void 0
                                        : r.length) &&
                                    ((t = s),
                                    this._layouts[s].forEach((t) => {
                                        const e = i.find(
                                            (e) => e._id === t._id
                                        );
                                        e &&
                                            ((e.x = t.x),
                                            (e.y = t.y),
                                            (e.w = t.w));
                                    }));
                            }
                            if (
                                (a.forEach((t) => {
                                    const e = i.findIndex(
                                        (e) => e._id === t._id
                                    );
                                    e !== -1 &&
                                        ((i[e].x = t.x),
                                        (i[e].y = t.y),
                                        (i[e].w = t.w),
                                        n.push(i[e]),
                                        i.splice(e, 1));
                                }),
                                i.length)
                            )
                                if (typeof o === "function") o(e, t, n, i);
                                else if (!l) {
                                    const s = e / t,
                                        r = o === "move" || o === "moveScale",
                                        l = o === "scale" || o === "moveScale";
                                    i.forEach((i) => {
                                        (i.x =
                                            e === 1
                                                ? 0
                                                : r
                                                ? Math.round(i.x * s)
                                                : Math.min(i.x, e - 1)),
                                            (i.w =
                                                e === 1 || t === 1
                                                    ? 1
                                                    : l
                                                    ? Math.round(i.w * s) || 1
                                                    : Math.min(i.w, e)),
                                            n.push(i);
                                    }),
                                        (i = []);
                                }
                            return (
                                (n = s.Utils.sort(n, -1, e)),
                                (this._inColumnResize = !0),
                                (this.nodes = []),
                                n.forEach((t) => {
                                    this.addNode(t, !1), delete t._orig;
                                }),
                                this.commit(),
                                delete this._inColumnResize,
                                this
                            );
                        }
                        cacheLayout(t, e, i = !1) {
                            const s = [];
                            return (
                                t.forEach((t, e) => {
                                    (t._id = t._id || o._idSeq++),
                                        (s[e] = {
                                            x: t.x,
                                            y: t.y,
                                            w: t.w,
                                            _id: t._id,
                                        });
                                }),
                                (this._layouts = i ? [] : this._layouts || []),
                                (this._layouts[e] = s),
                                this
                            );
                        }
                        cacheOneLayout(t, e) {
                            t._id = t._id || o._idSeq++;
                            const i = { x: t.x, y: t.y, w: t.w, _id: t._id };
                            (this._layouts = this._layouts || []),
                                (this._layouts[e] = this._layouts[e] || []);
                            const s = this._layouts[e].findIndex(
                                (e) => e._id === t._id
                            );
                            return (
                                s === -1
                                    ? this._layouts[e].push(i)
                                    : (this._layouts[e][s] = i),
                                this
                            );
                        }
                        cleanupNode(t) {
                            for (const e in t)
                                e[0] === "_" && e !== "_id" && delete t[e];
                            return this;
                        }
                    }
                    (e.GridStackEngine = o), (o._idSeq = 1);
                },
                930: function (t, e, i) {
                    var s =
                            (this && this.__createBinding) ||
                            (Object.create
                                ? function (t, e, i, s) {
                                      void 0 === s && (s = i),
                                          Object.defineProperty(t, s, {
                                              enumerable: !0,
                                              get: function () {
                                                  return e[i];
                                              },
                                          });
                                  }
                                : function (t, e, i, s) {
                                      void 0 === s && (s = i), (t[s] = e[i]);
                                  }),
                        o =
                            (this && this.__exportStar) ||
                            function (t, e) {
                                for (var i in t)
                                    i === "default" ||
                                        e.hasOwnProperty(i) ||
                                        s(e, t, i);
                            };
                    Object.defineProperty(e, "__esModule", { value: !0 }),
                        o(i(699), e),
                        o(i(593), e),
                        o(i(62), e),
                        o(i(334), e),
                        o(i(270), e),
                        o(i(761), e);
                },
                270: function (t, e, i) {
                    var s =
                            (this && this.__createBinding) ||
                            (Object.create
                                ? function (t, e, i, s) {
                                      void 0 === s && (s = i),
                                          Object.defineProperty(t, s, {
                                              enumerable: !0,
                                              get: function () {
                                                  return e[i];
                                              },
                                          });
                                  }
                                : function (t, e, i, s) {
                                      void 0 === s && (s = i), (t[s] = e[i]);
                                  }),
                        o =
                            (this && this.__exportStar) ||
                            function (t, e) {
                                for (var i in t)
                                    i === "default" ||
                                        e.hasOwnProperty(i) ||
                                        s(e, t, i);
                            };
                    Object.defineProperty(e, "__esModule", { value: !0 }),
                        (e.GridStack = void 0);
                    const r = i(62),
                        n = i(593),
                        l = i(334);
                    o(i(699), e), o(i(593), e), o(i(62), e), o(i(334), e);
                    const a = {
                        column: 12,
                        minRow: 0,
                        maxRow: 0,
                        itemClass: "grid-stack-item",
                        placeholderClass: "grid-stack-placeholder",
                        placeholderText: "",
                        handle: ".grid-stack-item-content",
                        handleClass: null,
                        styleInHead: !1,
                        cellHeight: "auto",
                        cellHeightThrottle: 100,
                        margin: 10,
                        auto: !0,
                        minWidth: 768,
                        float: !1,
                        staticGrid: !1,
                        animate: !0,
                        alwaysShowResizeHandle: !1,
                        resizable: { autoHide: !0, handles: "se" },
                        draggable: {
                            handle: ".grid-stack-item-content",
                            scroll: !1,
                            appendTo: "body",
                        },
                        disableDrag: !1,
                        disableResize: !1,
                        rtl: "auto",
                        removable: !1,
                        removableOptions: { accept: ".grid-stack-item" },
                        marginUnit: "px",
                        cellHeightUnit: "px",
                        disableOneColumnMode: !1,
                        oneColumnModeDomSort: !1,
                    };
                    class h {
                        constructor(t, e = {}) {
                            (this._gsEventHandler = {}),
                                (this._extraDragRow = 0),
                                (this.el = t),
                                (e = e || {}).row &&
                                    ((e.minRow = e.maxRow = e.row),
                                    delete e.row);
                            const i = n.Utils.toNumber(
                                    t.getAttribute("gs-row")
                                ),
                                s = Object.assign(
                                    Object.assign({}, n.Utils.cloneDeep(a)),
                                    {
                                        column:
                                            n.Utils.toNumber(
                                                t.getAttribute("gs-column")
                                            ) || 12,
                                        minRow:
                                            i ||
                                            n.Utils.toNumber(
                                                t.getAttribute("gs-min-row")
                                            ) ||
                                            0,
                                        maxRow:
                                            i ||
                                            n.Utils.toNumber(
                                                t.getAttribute("gs-max-row")
                                            ) ||
                                            0,
                                        staticGrid:
                                            n.Utils.toBool(
                                                t.getAttribute("gs-static")
                                            ) || !1,
                                        _styleSheetClass:
                                            "grid-stack-instance-" +
                                            (1e4 * Math.random()).toFixed(0),
                                        alwaysShowResizeHandle:
                                            e.alwaysShowResizeHandle || !1,
                                        resizable: {
                                            autoHide: !e.alwaysShowResizeHandle,
                                            handles: "se",
                                        },
                                        draggable: {
                                            handle:
                                                (e.handleClass
                                                    ? "." + e.handleClass
                                                    : e.handle
                                                    ? e.handle
                                                    : "") ||
                                                ".grid-stack-item-content",
                                            scroll: !1,
                                            appendTo: "body",
                                        },
                                        removableOptions: {
                                            accept:
                                                "." +
                                                (e.itemClass ||
                                                    "grid-stack-item"),
                                        },
                                    }
                                );
                            t.getAttribute("gs-animate") &&
                                (s.animate = n.Utils.toBool(
                                    t.getAttribute("gs-animate")
                                )),
                                (this.opts = n.Utils.defaults(e, s)),
                                (e = null),
                                this.initMargin(),
                                this.opts.column !== 1 &&
                                    !this.opts.disableOneColumnMode &&
                                    this._widthOrContainer() <=
                                        this.opts.minWidth &&
                                    ((this._prevColumn = this.opts.column),
                                    (this.opts.column = 1)),
                                this.opts.rtl === "auto" &&
                                    (this.opts.rtl =
                                        t.style.direction === "rtl"),
                                this.opts.rtl &&
                                    this.el.classList.add("grid-stack-rtl");
                            const o = n.Utils.closestByClass(
                                this.el,
                                a.itemClass
                            );
                            if (
                                (o &&
                                    o.gridstackNode &&
                                    ((this.opts._isNested = o.gridstackNode),
                                    (this.opts._isNested.subGrid = this),
                                    this.el.classList.add("grid-stack-nested")),
                                (this._isAutoCellHeight =
                                    this.opts.cellHeight === "auto"),
                                this._isAutoCellHeight ||
                                this.opts.cellHeight === "initial"
                                    ? this.cellHeight(void 0, !1)
                                    : (typeof this.opts.cellHeight ===
                                          "number" &&
                                          this.opts.cellHeightUnit &&
                                          this.opts.cellHeightUnit !==
                                              a.cellHeightUnit &&
                                          ((this.opts.cellHeight =
                                              this.opts.cellHeight +
                                              this.opts.cellHeightUnit),
                                          delete this.opts.cellHeightUnit),
                                      this.cellHeight(
                                          this.opts.cellHeight,
                                          !1
                                      )),
                                this.el.classList.add(
                                    this.opts._styleSheetClass
                                ),
                                this._setStaticClass(),
                                (this.engine = new r.GridStackEngine({
                                    column: this.opts.column,
                                    float: this.opts.float,
                                    maxRow: this.opts.maxRow,
                                    onChange: (t) => {
                                        let e = 0;
                                        this.engine.nodes.forEach((t) => {
                                            e = Math.max(e, t.y + t.h);
                                        }),
                                            t.forEach((t) => {
                                                const e = t.el;
                                                e &&
                                                    (t._removeDOM
                                                        ? (e && e.remove(),
                                                          delete t._removeDOM)
                                                        : this._writePosAttr(
                                                              e,
                                                              t
                                                          ));
                                            }),
                                            this._updateStyles(!1, e);
                                    },
                                })),
                                this.opts.auto)
                            ) {
                                this.batchUpdate();
                                const t = [];
                                this.getGridItems().forEach((e) => {
                                    const i = parseInt(e.getAttribute("gs-x")),
                                        s = parseInt(e.getAttribute("gs-y"));
                                    t.push({
                                        el: e,
                                        i:
                                            (Number.isNaN(i) ? 1e3 : i) +
                                            (Number.isNaN(s) ? 1e3 : s) *
                                                this.opts.column,
                                    });
                                }),
                                    t
                                        .sort((t, e) => t.i - e.i)
                                        .forEach((t) =>
                                            this._prepareElement(t.el)
                                        ),
                                    this.commit();
                            }
                            this.setAnimation(this.opts.animate),
                                this._updateStyles(),
                                this.opts.column != 12 &&
                                    this.el.classList.add(
                                        "grid-stack-" + this.opts.column
                                    ),
                                this.opts.dragIn &&
                                    h.setupDragIn(
                                        this.opts.dragIn,
                                        this.opts.dragInOptions
                                    ),
                                delete this.opts.dragIn,
                                delete this.opts.dragInOptions,
                                this._setupRemoveDrop(),
                                this._setupAcceptWidget(),
                                this._updateWindowResizeEvent();
                        }
                        static init(t = {}, e = ".grid-stack") {
                            const i = h.getGridElement(e);
                            return i
                                ? (i.gridstack ||
                                      (i.gridstack = new h(
                                          i,
                                          n.Utils.cloneDeep(t)
                                      )),
                                  i.gridstack)
                                : (typeof e === "string"
                                      ? console.error(
                                            'GridStack.initAll() no grid was found with selector "' +
                                                e +
                                                '" - element missing or wrong selector ?\nNote: ".grid-stack" is required for proper CSS styling and drag/drop, and is the default selector.'
                                        )
                                      : console.error(
                                            "GridStack.init() no grid element was passed."
                                        ),
                                  null);
                        }
                        static initAll(t = {}, e = ".grid-stack") {
                            const i = [];
                            return (
                                h.getGridElements(e).forEach((e) => {
                                    e.gridstack ||
                                        ((e.gridstack = new h(
                                            e,
                                            n.Utils.cloneDeep(t)
                                        )),
                                        delete t.dragIn,
                                        delete t.dragInOptions),
                                        i.push(e.gridstack);
                                }),
                                i.length === 0 &&
                                    console.error(
                                        'GridStack.initAll() no grid was found with selector "' +
                                            e +
                                            '" - element missing or wrong selector ?\nNote: ".grid-stack" is required for proper CSS styling and drag/drop, and is the default selector.'
                                    ),
                                i
                            );
                        }
                        static addGrid(t, e = {}) {
                            if (!t) return null;
                            let i = t;
                            if (!t.classList.contains("grid-stack")) {
                                const s =
                                    document.implementation.createHTMLDocument(
                                        ""
                                    );
                                (s.body.innerHTML = `<div class="grid-stack ${
                                    e.class || ""
                                }"></div>`),
                                    (i = s.body.children[0]),
                                    t.appendChild(i);
                            }
                            const s = h.init(e, i);
                            if (s.opts.children) {
                                const t = s.opts.children;
                                delete s.opts.children, s.load(t);
                            }
                            return s;
                        }
                        get placeholder() {
                            if (!this._placeholder) {
                                const t = document.createElement("div");
                                (t.className = "placeholder-content"),
                                    this.opts.placeholderText &&
                                        (t.innerHTML =
                                            this.opts.placeholderText),
                                    (this._placeholder =
                                        document.createElement("div")),
                                    this._placeholder.classList.add(
                                        this.opts.placeholderClass,
                                        a.itemClass,
                                        this.opts.itemClass
                                    ),
                                    this.placeholder.appendChild(t);
                            }
                            return this._placeholder;
                        }
                        addWidget(t, e) {
                            if (arguments.length > 2) {
                                console.warn(
                                    "gridstack.ts: `addWidget(el, x, y, width...)` is deprecated. Use `addWidget({x, y, w, content, ...})`. It will be removed soon"
                                );
                                let e = arguments,
                                    i = 1,
                                    s = {
                                        x: e[i++],
                                        y: e[i++],
                                        w: e[i++],
                                        h: e[i++],
                                        autoPosition: e[i++],
                                        minW: e[i++],
                                        maxW: e[i++],
                                        minH: e[i++],
                                        maxH: e[i++],
                                        id: e[i++],
                                    };
                                return this.addWidget(t, s);
                            }
                            let i;
                            if (typeof t === "string") {
                                const e =
                                    document.implementation.createHTMLDocument(
                                        ""
                                    );
                                (e.body.innerHTML = t),
                                    (i = e.body.children[0]);
                            } else if (
                                arguments.length === 0 ||
                                (arguments.length === 1 &&
                                    (void 0 !== (s = t).x ||
                                        void 0 !== s.y ||
                                        void 0 !== s.w ||
                                        void 0 !== s.h ||
                                        void 0 !== s.content))
                            ) {
                                const s = (t && t.content) || "";
                                e = t;
                                const o =
                                    document.implementation.createHTMLDocument(
                                        ""
                                    );
                                (o.body.innerHTML = `<div class="grid-stack-item ${
                                    this.opts.itemClass || ""
                                }"><div class="grid-stack-item-content">${s}</div></div>`),
                                    (i = o.body.children[0]);
                            } else i = t;
                            var s;
                            const o = this._readAttr(i);
                            (e = n.Utils.cloneDeep(e) || {}),
                                n.Utils.defaults(e, o);
                            const r = this.engine.prepareNode(e);
                            if (
                                (this._writeAttr(i, e),
                                this._insertNotAppend
                                    ? this.el.prepend(i)
                                    : this.el.appendChild(i),
                                this._prepareElement(i, !0, e),
                                this._updateContainerHeight(),
                                r.subGrid && !r.subGrid.el)
                            ) {
                                const t = r.el.querySelector(
                                    ".grid-stack-item-content"
                                );
                                r.subGrid = h.addGrid(t, r.subGrid);
                            }
                            return (
                                this._triggerAddEvent(),
                                this._triggerChangeEvent(),
                                i
                            );
                        }
                        save(t = !0, e = !1) {
                            const i = this.engine.save(t);
                            if (
                                (i.forEach((e) => {
                                    if (t && e.el && !e.subGrid) {
                                        const t = e.el.querySelector(
                                            ".grid-stack-item-content"
                                        );
                                        (e.content = t ? t.innerHTML : void 0),
                                            e.content || delete e.content;
                                    } else
                                        t || delete e.content,
                                            e.subGrid &&
                                                (e.subGrid = e.subGrid.save(
                                                    t,
                                                    !0
                                                ));
                                    delete e.el;
                                }),
                                e)
                            ) {
                                const t = n.Utils.cloneDeep(this.opts);
                                return (
                                    t.marginBottom === t.marginTop &&
                                        t.marginRight === t.marginLeft &&
                                        t.marginTop === t.marginRight &&
                                        ((t.margin = t.marginTop),
                                        delete t.marginTop,
                                        delete t.marginRight,
                                        delete t.marginBottom,
                                        delete t.marginLeft),
                                    t.rtl ===
                                        (this.el.style.direction === "rtl") &&
                                        (t.rtl = "auto"),
                                    this._isAutoCellHeight &&
                                        (t.cellHeight = "auto"),
                                    n.Utils.removeInternalAndSame(t, a),
                                    (t.children = i),
                                    t
                                );
                            }
                            return i;
                        }
                        load(t, e = !0) {
                            const i = h.Utils.sort(
                                [...t],
                                -1,
                                this._prevColumn || this.opts.column
                            );
                            (this._insertNotAppend = !0),
                                this._prevColumn &&
                                    this._prevColumn !== this.opts.column &&
                                    i.some(
                                        (t) => t.x + t.w > this.opts.column
                                    ) &&
                                    ((this._ignoreLayoutsNodeChange = !0),
                                    this.engine.cacheLayout(
                                        i,
                                        this._prevColumn,
                                        !0
                                    ));
                            const s = [];
                            return (
                                this.batchUpdate(),
                                e &&
                                    [...this.engine.nodes].forEach((t) => {
                                        i.find((e) => t.id === e.id) ||
                                            (typeof e === "function"
                                                ? e(this, t, !1)
                                                : (s.push(t),
                                                  this.removeWidget(
                                                      t.el,
                                                      !0,
                                                      !1
                                                  )));
                                    }),
                                i.forEach((t) => {
                                    const i =
                                        t.id || t.id === 0
                                            ? this.engine.nodes.find(
                                                  (e) => e.id === t.id
                                              )
                                            : void 0;
                                    if (i) {
                                        if (
                                            (this.update(i.el, t),
                                            t.subGrid && t.subGrid.children)
                                        ) {
                                            const e =
                                                i.el.querySelector(
                                                    ".grid-stack"
                                                );
                                            e &&
                                                e.gridstack &&
                                                (e.gridstack.load(
                                                    t.subGrid.children
                                                ),
                                                (this._insertNotAppend = !0));
                                        }
                                    } else
                                        e &&
                                            (t =
                                                typeof e === "function"
                                                    ? e(this, t, !0)
                                                          .gridstackNode
                                                    : this.addWidget(t)
                                                          .gridstackNode);
                                }),
                                (this.engine.removedNodes = s),
                                this.commit(),
                                delete this._ignoreLayoutsNodeChange,
                                delete this._insertNotAppend,
                                this
                            );
                        }
                        batchUpdate() {
                            return this.engine.batchUpdate(), this;
                        }
                        getCellHeight(t = !1) {
                            return !this.opts.cellHeight ||
                                this.opts.cellHeight === "auto" ||
                                (t &&
                                    this.opts.cellHeightUnit &&
                                    this.opts.cellHeightUnit !== "px")
                                ? Math.round(
                                      this.el.getBoundingClientRect().height
                                  ) /
                                      parseInt(
                                          this.el.getAttribute("gs-current-row")
                                      )
                                : this.opts.cellHeight;
                        }
                        cellHeight(t, e = !0) {
                            if (
                                (e &&
                                    void 0 !== t &&
                                    this._isAutoCellHeight !== (t === "auto") &&
                                    ((this._isAutoCellHeight = t === "auto"),
                                    this._updateWindowResizeEvent()),
                                (t !== "initial" && t !== "auto") ||
                                    (t = void 0),
                                void 0 === t)
                            ) {
                                const e =
                                    -this.opts.marginRight -
                                    this.opts.marginLeft +
                                    this.opts.marginTop +
                                    this.opts.marginBottom;
                                t = this.cellWidth() + e;
                            }
                            const i = n.Utils.parseHeight(t);
                            return (
                                (this.opts.cellHeightUnit === i.unit &&
                                    this.opts.cellHeight === i.h) ||
                                    ((this.opts.cellHeightUnit = i.unit),
                                    (this.opts.cellHeight = i.h),
                                    e && this._updateStyles(!0, this.getRow())),
                                this
                            );
                        }
                        cellWidth() {
                            return this._widthOrContainer() / this.opts.column;
                        }
                        _widthOrContainer() {
                            return (
                                this.el.clientWidth ||
                                this.el.parentElement.clientWidth ||
                                window.innerWidth
                            );
                        }
                        commit() {
                            return (
                                this.engine.commit(),
                                this._triggerRemoveEvent(),
                                this._triggerAddEvent(),
                                this._triggerChangeEvent(),
                                this
                            );
                        }
                        compact() {
                            return (
                                this.engine.compact(),
                                this._triggerChangeEvent(),
                                this
                            );
                        }
                        column(t, e = "moveScale") {
                            if (t < 1 || this.opts.column === t) return this;
                            let i,
                                s = this.opts.column;
                            return (
                                t === 1
                                    ? (this._prevColumn = s)
                                    : delete this._prevColumn,
                                this.el.classList.remove("grid-stack-" + s),
                                this.el.classList.add("grid-stack-" + t),
                                (this.opts.column = this.engine.column = t),
                                t === 1 &&
                                    this.opts.oneColumnModeDomSort &&
                                    ((i = []),
                                    this.getGridItems().forEach((t) => {
                                        t.gridstackNode &&
                                            i.push(t.gridstackNode);
                                    }),
                                    i.length || (i = void 0)),
                                this.engine.updateNodeWidths(s, t, i, e),
                                this._isAutoCellHeight && this.cellHeight(),
                                (this._ignoreLayoutsNodeChange = !0),
                                this._triggerChangeEvent(),
                                delete this._ignoreLayoutsNodeChange,
                                this
                            );
                        }
                        getColumn() {
                            return this.opts.column;
                        }
                        getGridItems() {
                            return Array.from(this.el.children).filter(
                                (t) =>
                                    t.matches("." + this.opts.itemClass) &&
                                    !t.matches("." + this.opts.placeholderClass)
                            );
                        }
                        destroy(t = !0) {
                            if (this.el)
                                return (
                                    this._updateWindowResizeEvent(!0),
                                    this.setStatic(!0, !1),
                                    this.setAnimation(!1),
                                    t
                                        ? this.el.parentNode.removeChild(
                                              this.el
                                          )
                                        : (this.removeAll(t),
                                          this.el.classList.remove(
                                              this.opts._styleSheetClass
                                          )),
                                    this._removeStylesheet(),
                                    this.el.removeAttribute("gs-current-row"),
                                    delete this.opts._isNested,
                                    delete this.opts,
                                    delete this._placeholder,
                                    delete this.engine,
                                    delete this.el.gridstack,
                                    delete this.el,
                                    this
                                );
                        }
                        float(t) {
                            return (
                                (this.engine.float = t),
                                this._triggerChangeEvent(),
                                this
                            );
                        }
                        getFloat() {
                            return this.engine.float;
                        }
                        getCellFromPixel(t, e = !1) {
                            let i,
                                s = this.el.getBoundingClientRect();
                            i = e
                                ? {
                                      top:
                                          s.top +
                                          document.documentElement.scrollTop,
                                      left: s.left,
                                  }
                                : {
                                      top: this.el.offsetTop,
                                      left: this.el.offsetLeft,
                                  };
                            const o = t.left - i.left,
                                r = t.top - i.top,
                                n = s.width / this.opts.column,
                                l =
                                    s.height /
                                    parseInt(
                                        this.el.getAttribute("gs-current-row")
                                    );
                            return {
                                x: Math.floor(o / n),
                                y: Math.floor(r / l),
                            };
                        }
                        getRow() {
                            return Math.max(
                                this.engine.getRow(),
                                this.opts.minRow
                            );
                        }
                        isAreaEmpty(t, e, i, s) {
                            return this.engine.isAreaEmpty(t, e, i, s);
                        }
                        makeWidget(t) {
                            const e = h.getElement(t);
                            return (
                                this._prepareElement(e, !0),
                                this._updateContainerHeight(),
                                this._triggerAddEvent(),
                                this._triggerChangeEvent(),
                                e
                            );
                        }
                        on(t, e) {
                            if (t.indexOf(" ") !== -1)
                                return (
                                    t.split(" ").forEach((t) => this.on(t, e)),
                                    this
                                );
                            if (
                                t === "change" ||
                                t === "added" ||
                                t === "removed" ||
                                t === "enable" ||
                                t === "disable"
                            ) {
                                const i = t === "enable" || t === "disable";
                                (this._gsEventHandler[t] = i
                                    ? (t) => e(t)
                                    : (t) => e(t, t.detail)),
                                    this.el.addEventListener(
                                        t,
                                        this._gsEventHandler[t]
                                    );
                            } else
                                t === "drag" ||
                                t === "dragstart" ||
                                t === "dragstop" ||
                                t === "resizestart" ||
                                t === "resize" ||
                                t === "resizestop" ||
                                t === "dropped"
                                    ? (this._gsEventHandler[t] = e)
                                    : console.log(
                                          "GridStack.on(" +
                                              t +
                                              ') event not supported, but you can still use $(".grid-stack").on(...) while jquery-ui is still used internally.'
                                      );
                            return this;
                        }
                        off(t) {
                            return t.indexOf(" ") !== -1
                                ? (t.split(" ").forEach((t) => this.off(t)),
                                  this)
                                : ((t !== "change" &&
                                      t !== "added" &&
                                      t !== "removed" &&
                                      t !== "enable" &&
                                      t !== "disable") ||
                                      (this._gsEventHandler[t] &&
                                          this.el.removeEventListener(
                                              t,
                                              this._gsEventHandler[t]
                                          )),
                                  delete this._gsEventHandler[t],
                                  this);
                        }
                        removeWidget(t, e = !0, i = !0) {
                            return (
                                h.getElements(t).forEach((t) => {
                                    if (t.parentElement !== this.el) return;
                                    let s = t.gridstackNode;
                                    s ||
                                        (s = this.engine.nodes.find(
                                            (e) => t === e.el
                                        )),
                                        s &&
                                            (delete t.gridstackNode,
                                            l.GridStackDDI.get().remove(t),
                                            this.engine.removeNode(s, e, i),
                                            e && t.parentElement && t.remove());
                                }),
                                i &&
                                    (this._triggerRemoveEvent(),
                                    this._triggerChangeEvent()),
                                this
                            );
                        }
                        removeAll(t = !0) {
                            return (
                                this.engine.nodes.forEach((t) => {
                                    delete t.el.gridstackNode,
                                        l.GridStackDDI.get().remove(t.el);
                                }),
                                this.engine.removeAll(t),
                                this._triggerRemoveEvent(),
                                this
                            );
                        }
                        setAnimation(t) {
                            return (
                                t
                                    ? this.el.classList.add(
                                          "grid-stack-animate"
                                      )
                                    : this.el.classList.remove(
                                          "grid-stack-animate"
                                      ),
                                this
                            );
                        }
                        setStatic(t, e = !0) {
                            return (
                                this.opts.staticGrid === t ||
                                    ((this.opts.staticGrid = t),
                                    this._setupRemoveDrop(),
                                    this._setupAcceptWidget(),
                                    this.engine.nodes.forEach((t) =>
                                        this._prepareDragDropByNode(t)
                                    ),
                                    e && this._setStaticClass()),
                                this
                            );
                        }
                        update(t, e) {
                            if (arguments.length > 2) {
                                console.warn(
                                    "gridstack.ts: `update(el, x, y, w, h)` is deprecated. Use `update(el, {x, w, content, ...})`. It will be removed soon"
                                );
                                let i = arguments,
                                    s = 1;
                                return (
                                    (e = {
                                        x: i[s++],
                                        y: i[s++],
                                        w: i[s++],
                                        h: i[s++],
                                    }),
                                    this.update(t, e)
                                );
                            }
                            return (
                                h.getElements(t).forEach((t) => {
                                    if (!t || !t.gridstackNode) return;
                                    const i = t.gridstackNode,
                                        s = n.Utils.cloneDeep(e);
                                    delete s.autoPosition;
                                    let o,
                                        r = ["x", "y", "w", "h"];
                                    if (
                                        (r.some(
                                            (t) =>
                                                void 0 !== s[t] && s[t] !== i[t]
                                        ) &&
                                            ((o = {}),
                                            r.forEach((t) => {
                                                (o[t] =
                                                    void 0 !== s[t]
                                                        ? s[t]
                                                        : i[t]),
                                                    delete s[t];
                                            })),
                                        !o &&
                                            (s.minW ||
                                                s.minH ||
                                                s.maxW ||
                                                s.maxH) &&
                                            (o = {}),
                                        s.content)
                                    ) {
                                        const e = t.querySelector(
                                            ".grid-stack-item-content"
                                        );
                                        e &&
                                            e.innerHTML !== s.content &&
                                            (e.innerHTML = s.content),
                                            delete s.content;
                                    }
                                    let l = !1,
                                        a = !1;
                                    for (const t in s)
                                        t[0] !== "_" &&
                                            i[t] !== s[t] &&
                                            ((i[t] = s[t]),
                                            (l = !0),
                                            (a =
                                                a ||
                                                (!this.opts.staticGrid &&
                                                    (t === "noResize" ||
                                                        t === "noMove" ||
                                                        t === "locked"))));
                                    o &&
                                        (this.engine
                                            .cleanNodes()
                                            .beginUpdate(i)
                                            .moveNode(i, o),
                                        this._updateContainerHeight(),
                                        this._triggerChangeEvent(),
                                        this.engine.endUpdate()),
                                        l && this._writeAttr(t, i),
                                        a && this._prepareDragDropByNode(i);
                                }),
                                this
                            );
                        }
                        margin(t) {
                            if (
                                !(
                                    typeof t === "string" &&
                                    t.split(" ").length > 1
                                )
                            ) {
                                const e = n.Utils.parseHeight(t);
                                if (
                                    this.opts.marginUnit === e.unit &&
                                    this.opts.margin === e.h
                                )
                                    return;
                            }
                            return (
                                (this.opts.margin = t),
                                (this.opts.marginTop =
                                    this.opts.marginBottom =
                                    this.opts.marginLeft =
                                    this.opts.marginRight =
                                        void 0),
                                this.initMargin(),
                                this._updateStyles(!0),
                                this
                            );
                        }
                        getMargin() {
                            return this.opts.margin;
                        }
                        willItFit(t) {
                            if (arguments.length > 1) {
                                console.warn(
                                    "gridstack.ts: `willItFit(x,y,w,h,autoPosition)` is deprecated. Use `willItFit({x, y,...})`. It will be removed soon"
                                );
                                let t = arguments,
                                    e = 0,
                                    i = {
                                        x: t[e++],
                                        y: t[e++],
                                        w: t[e++],
                                        h: t[e++],
                                        autoPosition: t[e++],
                                    };
                                return this.willItFit(i);
                            }
                            return this.engine.willItFit(t);
                        }
                        _triggerChangeEvent() {
                            if (this.engine.batchMode) return this;
                            const t = this.engine.getDirtyNodes(!0);
                            return (
                                t &&
                                    t.length &&
                                    (this._ignoreLayoutsNodeChange ||
                                        this.engine.layoutsNodesChange(t),
                                    this._triggerEvent("change", t)),
                                this.engine.saveInitial(),
                                this
                            );
                        }
                        _triggerAddEvent() {
                            return (
                                this.engine.batchMode ||
                                    (this.engine.addedNodes &&
                                        this.engine.addedNodes.length > 0 &&
                                        (this._ignoreLayoutsNodeChange ||
                                            this.engine.layoutsNodesChange(
                                                this.engine.addedNodes
                                            ),
                                        this.engine.addedNodes.forEach((t) => {
                                            delete t._dirty;
                                        }),
                                        this._triggerEvent(
                                            "added",
                                            this.engine.addedNodes
                                        ),
                                        (this.engine.addedNodes = []))),
                                this
                            );
                        }
                        _triggerRemoveEvent() {
                            return (
                                this.engine.batchMode ||
                                    (this.engine.removedNodes &&
                                        this.engine.removedNodes.length > 0 &&
                                        (this._triggerEvent(
                                            "removed",
                                            this.engine.removedNodes
                                        ),
                                        (this.engine.removedNodes = []))),
                                this
                            );
                        }
                        _triggerEvent(t, e) {
                            const i = e
                                ? new CustomEvent(t, { bubbles: !1, detail: e })
                                : new Event(t);
                            return this.el.dispatchEvent(i), this;
                        }
                        _removeStylesheet() {
                            return (
                                this._styles &&
                                    (n.Utils.removeStylesheet(this._styles._id),
                                    delete this._styles),
                                this
                            );
                        }
                        _updateStyles(t = !1, e) {
                            if (
                                (t && this._removeStylesheet(),
                                this._updateContainerHeight(),
                                this.opts.cellHeight === 0)
                            )
                                return this;
                            const i = this.opts.cellHeight,
                                s = this.opts.cellHeightUnit,
                                o = `.${this.opts._styleSheetClass} > .${this.opts.itemClass}`;
                            if (!this._styles) {
                                const t =
                                        "gridstack-style-" +
                                        (1e5 * Math.random()).toFixed(),
                                    e = this.opts.styleInHead
                                        ? void 0
                                        : this.el.parentNode;
                                if (
                                    ((this._styles = n.Utils.createStylesheet(
                                        t,
                                        e
                                    )),
                                    !this._styles)
                                )
                                    return this;
                                (this._styles._id = t),
                                    (this._styles._max = 0),
                                    n.Utils.addCSSRule(
                                        this._styles,
                                        o,
                                        `min-height: ${i}${s}`
                                    );
                                const r =
                                        this.opts.marginTop +
                                        this.opts.marginUnit,
                                    l =
                                        this.opts.marginBottom +
                                        this.opts.marginUnit,
                                    a =
                                        this.opts.marginRight +
                                        this.opts.marginUnit,
                                    h =
                                        this.opts.marginLeft +
                                        this.opts.marginUnit,
                                    d = `${o} > .grid-stack-item-content`,
                                    g = `.${this.opts._styleSheetClass} > .grid-stack-placeholder > .placeholder-content`;
                                n.Utils.addCSSRule(
                                    this._styles,
                                    d,
                                    `top: ${r}; right: ${a}; bottom: ${l}; left: ${h};`
                                ),
                                    n.Utils.addCSSRule(
                                        this._styles,
                                        g,
                                        `top: ${r}; right: ${a}; bottom: ${l}; left: ${h};`
                                    ),
                                    n.Utils.addCSSRule(
                                        this._styles,
                                        `${o} > .ui-resizable-ne`,
                                        `right: ${a}`
                                    ),
                                    n.Utils.addCSSRule(
                                        this._styles,
                                        `${o} > .ui-resizable-e`,
                                        `right: ${a}`
                                    ),
                                    n.Utils.addCSSRule(
                                        this._styles,
                                        `${o} > .ui-resizable-se`,
                                        `right: ${a}; bottom: ${l}`
                                    ),
                                    n.Utils.addCSSRule(
                                        this._styles,
                                        `${o} > .ui-resizable-nw`,
                                        `left: ${h}`
                                    ),
                                    n.Utils.addCSSRule(
                                        this._styles,
                                        `${o} > .ui-resizable-w`,
                                        `left: ${h}`
                                    ),
                                    n.Utils.addCSSRule(
                                        this._styles,
                                        `${o} > .ui-resizable-sw`,
                                        `left: ${h}; bottom: ${l}`
                                    );
                            }
                            if (
                                (e = e || this._styles._max) > this._styles._max
                            ) {
                                const t = (t) => i * t + s;
                                for (
                                    let i = this._styles._max + 1;
                                    i <= e;
                                    i++
                                ) {
                                    const e = t(i);
                                    n.Utils.addCSSRule(
                                        this._styles,
                                        `${o}[gs-y="${i - 1}"]`,
                                        `top: ${t(i - 1)}`
                                    ),
                                        n.Utils.addCSSRule(
                                            this._styles,
                                            `${o}[gs-h="${i}"]`,
                                            `height: ${e}`
                                        ),
                                        n.Utils.addCSSRule(
                                            this._styles,
                                            `${o}[gs-min-h="${i}"]`,
                                            `min-height: ${e}`
                                        ),
                                        n.Utils.addCSSRule(
                                            this._styles,
                                            `${o}[gs-max-h="${i}"]`,
                                            `max-height: ${e}`
                                        );
                                }
                                this._styles._max = e;
                            }
                            return this;
                        }
                        _updateContainerHeight() {
                            if (!this.engine || this.engine.batchMode)
                                return this;
                            let t = this.getRow() + this._extraDragRow,
                                e = parseInt(
                                    getComputedStyle(this.el)["min-height"]
                                );
                            if (e > 0) {
                                const i = Math.round(
                                    e / this.getCellHeight(!0)
                                );
                                t < i && (t = i);
                            }
                            if (
                                (this.el.setAttribute(
                                    "gs-current-row",
                                    String(t)
                                ),
                                t === 0)
                            )
                                return (
                                    this.el.style.removeProperty("height"), this
                                );
                            const i = this.opts.cellHeight,
                                s = this.opts.cellHeightUnit;
                            return i
                                ? ((this.el.style.height = t * i + s), this)
                                : this;
                        }
                        _prepareElement(t, e = !1, i) {
                            i ||
                                (t.classList.add(this.opts.itemClass),
                                (i = this._readAttr(t))),
                                (t.gridstackNode = i),
                                (i.el = t),
                                (i.grid = this);
                            const s = Object.assign({}, i);
                            return (
                                (i = this.engine.addNode(i, e)),
                                n.Utils.same(i, s) || this._writeAttr(t, i),
                                this._prepareDragDropByNode(i),
                                this
                            );
                        }
                        _writePosAttr(t, e) {
                            return (
                                void 0 !== e.x &&
                                    e.x !== null &&
                                    t.setAttribute("gs-x", String(e.x)),
                                void 0 !== e.y &&
                                    e.y !== null &&
                                    t.setAttribute("gs-y", String(e.y)),
                                e.w && t.setAttribute("gs-w", String(e.w)),
                                e.h && t.setAttribute("gs-h", String(e.h)),
                                this
                            );
                        }
                        _writeAttr(t, e) {
                            if (!e) return this;
                            this._writePosAttr(t, e);
                            const i = {
                                autoPosition: "gs-auto-position",
                                minW: "gs-min-w",
                                minH: "gs-min-h",
                                maxW: "gs-max-w",
                                maxH: "gs-max-h",
                                noResize: "gs-no-resize",
                                noMove: "gs-no-move",
                                locked: "gs-locked",
                                id: "gs-id",
                                resizeHandles: "gs-resize-handles",
                            };
                            for (const s in i)
                                e[s]
                                    ? t.setAttribute(i[s], String(e[s]))
                                    : t.removeAttribute(i[s]);
                            return this;
                        }
                        _readAttr(t) {
                            const e = {};
                            (e.x = n.Utils.toNumber(t.getAttribute("gs-x"))),
                                (e.y = n.Utils.toNumber(
                                    t.getAttribute("gs-y")
                                )),
                                (e.w = n.Utils.toNumber(
                                    t.getAttribute("gs-w")
                                )),
                                (e.h = n.Utils.toNumber(
                                    t.getAttribute("gs-h")
                                )),
                                (e.maxW = n.Utils.toNumber(
                                    t.getAttribute("gs-max-w")
                                )),
                                (e.minW = n.Utils.toNumber(
                                    t.getAttribute("gs-min-w")
                                )),
                                (e.maxH = n.Utils.toNumber(
                                    t.getAttribute("gs-max-h")
                                )),
                                (e.minH = n.Utils.toNumber(
                                    t.getAttribute("gs-min-h")
                                )),
                                (e.autoPosition = n.Utils.toBool(
                                    t.getAttribute("gs-auto-position")
                                )),
                                (e.noResize = n.Utils.toBool(
                                    t.getAttribute("gs-no-resize")
                                )),
                                (e.noMove = n.Utils.toBool(
                                    t.getAttribute("gs-no-move")
                                )),
                                (e.locked = n.Utils.toBool(
                                    t.getAttribute("gs-locked")
                                )),
                                (e.resizeHandles =
                                    t.getAttribute("gs-resize-handles")),
                                (e.id = t.getAttribute("gs-id"));
                            for (const t in e) {
                                if (!e.hasOwnProperty(t)) return;
                                e[t] || e[t] === 0 || delete e[t];
                            }
                            return e;
                        }
                        _setStaticClass() {
                            const t = ["grid-stack-static"];
                            return (
                                this.opts.staticGrid
                                    ? (this.el.classList.add(...t),
                                      this.el.setAttribute("gs-static", "true"))
                                    : (this.el.classList.remove(...t),
                                      this.el.removeAttribute("gs-static")),
                                this
                            );
                        }
                        onParentResize() {
                            if (!this.el || !this.el.clientWidth) return;
                            let t =
                                    !this.opts.disableOneColumnMode &&
                                    this.el.clientWidth <= this.opts.minWidth,
                                e = !1;
                            return (
                                (this.opts.column === 1) !== t &&
                                    ((e = !0),
                                    this.opts.animate && this.setAnimation(!1),
                                    this.column(t ? 1 : this._prevColumn),
                                    this.opts.animate && this.setAnimation(!0)),
                                this._isAutoCellHeight &&
                                    (!e && this.opts.cellHeightThrottle
                                        ? (this._cellHeightThrottle ||
                                              (this._cellHeightThrottle =
                                                  n.Utils.throttle(
                                                      () => this.cellHeight(),
                                                      this.opts
                                                          .cellHeightThrottle
                                                  )),
                                          this._cellHeightThrottle())
                                        : this.cellHeight()),
                                this.engine.nodes.forEach((t) => {
                                    t.subGrid && t.subGrid.onParentResize();
                                }),
                                this
                            );
                        }
                        _updateWindowResizeEvent(t = !1) {
                            const e =
                                (this._isAutoCellHeight ||
                                    !this.opts.disableOneColumnMode) &&
                                !this.opts._isNested;
                            return (
                                t || !e || this._windowResizeBind
                                    ? (!t && e) ||
                                      !this._windowResizeBind ||
                                      (window.removeEventListener(
                                          "resize",
                                          this._windowResizeBind
                                      ),
                                      delete this._windowResizeBind)
                                    : ((this._windowResizeBind =
                                          this.onParentResize.bind(this)),
                                      window.addEventListener(
                                          "resize",
                                          this._windowResizeBind
                                      )),
                                this
                            );
                        }
                        static getElement(t = ".grid-stack-item") {
                            return n.Utils.getElement(t);
                        }
                        static getElements(t = ".grid-stack-item") {
                            return n.Utils.getElements(t);
                        }
                        static getGridElement(t) {
                            return h.getElement(t);
                        }
                        static getGridElements(t) {
                            return n.Utils.getElements(t);
                        }
                        initMargin() {
                            let t,
                                e = 0,
                                i = [];
                            return (
                                typeof this.opts.margin === "string" &&
                                    (i = this.opts.margin.split(" ")),
                                i.length === 2
                                    ? ((this.opts.marginTop =
                                          this.opts.marginBottom =
                                              i[0]),
                                      (this.opts.marginLeft =
                                          this.opts.marginRight =
                                              i[1]))
                                    : i.length === 4
                                    ? ((this.opts.marginTop = i[0]),
                                      (this.opts.marginRight = i[1]),
                                      (this.opts.marginBottom = i[2]),
                                      (this.opts.marginLeft = i[3]))
                                    : ((t = n.Utils.parseHeight(
                                          this.opts.margin
                                      )),
                                      (this.opts.marginUnit = t.unit),
                                      (e = this.opts.margin = t.h)),
                                void 0 === this.opts.marginTop
                                    ? (this.opts.marginTop = e)
                                    : ((t = n.Utils.parseHeight(
                                          this.opts.marginTop
                                      )),
                                      (this.opts.marginTop = t.h),
                                      delete this.opts.margin),
                                void 0 === this.opts.marginBottom
                                    ? (this.opts.marginBottom = e)
                                    : ((t = n.Utils.parseHeight(
                                          this.opts.marginBottom
                                      )),
                                      (this.opts.marginBottom = t.h),
                                      delete this.opts.margin),
                                void 0 === this.opts.marginRight
                                    ? (this.opts.marginRight = e)
                                    : ((t = n.Utils.parseHeight(
                                          this.opts.marginRight
                                      )),
                                      (this.opts.marginRight = t.h),
                                      delete this.opts.margin),
                                void 0 === this.opts.marginLeft
                                    ? (this.opts.marginLeft = e)
                                    : ((t = n.Utils.parseHeight(
                                          this.opts.marginLeft
                                      )),
                                      (this.opts.marginLeft = t.h),
                                      delete this.opts.margin),
                                (this.opts.marginUnit = t.unit),
                                this.opts.marginTop ===
                                    this.opts.marginBottom &&
                                    this.opts.marginLeft ===
                                        this.opts.marginRight &&
                                    this.opts.marginTop ===
                                        this.opts.marginRight &&
                                    (this.opts.margin = this.opts.marginTop),
                                this
                            );
                        }
                        static setupDragIn(t, e) {}
                        movable(t, e) {
                            return this;
                        }
                        resizable(t, e) {
                            return this;
                        }
                        disable() {
                            return this;
                        }
                        enable() {
                            return this;
                        }
                        enableMove(t) {
                            return this;
                        }
                        enableResize(t) {
                            return this;
                        }
                        _setupAcceptWidget() {
                            return this;
                        }
                        _setupRemoveDrop() {
                            return this;
                        }
                        _prepareDragDropByNode(t) {
                            return this;
                        }
                        _onStartMoving(t, e, i, s, o, r) {}
                        _dragOrResize(t, e, i, s, o, r) {}
                        _leave(t, e) {}
                    }
                    (e.GridStack = h),
                        (h.Utils = n.Utils),
                        (h.Engine = r.GridStackEngine);
                },
                861: (t, e) => {
                    Object.defineProperty(e, "__esModule", { value: !0 }),
                        (e.DDBaseImplement = void 0),
                        (e.DDBaseImplement = class {
                            constructor() {
                                (this._disabled = !1),
                                    (this._eventRegister = {});
                            }
                            get disabled() {
                                return this._disabled;
                            }
                            on(t, e) {
                                this._eventRegister[t] = e;
                            }
                            off(t) {
                                delete this._eventRegister[t];
                            }
                            enable() {
                                this._disabled = !1;
                            }
                            disable() {
                                this._disabled = !0;
                            }
                            destroy() {
                                delete this._eventRegister;
                            }
                            triggerEvent(t, e) {
                                if (
                                    !this.disabled &&
                                    this._eventRegister &&
                                    this._eventRegister[t]
                                )
                                    return this._eventRegister[t](e);
                            }
                        });
                },
                311: (t, e, i) => {
                    Object.defineProperty(e, "__esModule", { value: !0 }),
                        (e.DDDraggable = void 0);
                    const s = i(849),
                        o = i(943),
                        r = i(861);
                    class n extends r.DDBaseImplement {
                        constructor(t, e = {}) {
                            super(),
                                (this.dragging = !1),
                                (this.ui = () => {
                                    const t =
                                            this.el.parentElement.getBoundingClientRect(),
                                        e = this.helper.getBoundingClientRect();
                                    return {
                                        position: {
                                            top: e.top - t.top,
                                            left: e.left - t.left,
                                        },
                                    };
                                }),
                                (this.el = t),
                                (this.option = e);
                            const i = e.handle.substring(1);
                            (this.dragEl = t.classList.contains(i)
                                ? t
                                : t.querySelector(e.handle) || t),
                                (this._dragStart = this._dragStart.bind(this)),
                                (this._drag = this._drag.bind(this)),
                                (this._dragEnd = this._dragEnd.bind(this)),
                                this.enable();
                        }
                        on(t, e) {
                            super.on(t, e);
                        }
                        off(t) {
                            super.off(t);
                        }
                        enable() {
                            super.enable(),
                                (this.dragEl.draggable = !0),
                                this.dragEl.addEventListener(
                                    "dragstart",
                                    this._dragStart
                                ),
                                this.el.classList.remove(
                                    "ui-draggable-disabled"
                                ),
                                this.el.classList.add("ui-draggable");
                        }
                        disable(t = !1) {
                            super.disable(),
                                this.dragEl.removeAttribute("draggable"),
                                this.dragEl.removeEventListener(
                                    "dragstart",
                                    this._dragStart
                                ),
                                this.el.classList.remove("ui-draggable"),
                                t ||
                                    this.el.classList.add(
                                        "ui-draggable-disabled"
                                    );
                        }
                        destroy() {
                            this.dragging && this._dragEnd({}),
                                this.disable(!0),
                                delete this.el,
                                delete this.helper,
                                delete this.option,
                                super.destroy();
                        }
                        updateOption(t) {
                            return (
                                Object.keys(t).forEach(
                                    (e) => (this.option[e] = t[e])
                                ),
                                this
                            );
                        }
                        _dragStart(t) {
                            (s.DDManager.dragElement = this),
                                (this.helper = this._createHelper(t)),
                                this._setupHelperContainmentStyle(),
                                (this.dragOffset = this._getDragOffset(
                                    t,
                                    this.el,
                                    this.helperContainment
                                ));
                            const e = o.DDUtils.initEvent(t, {
                                target: this.el,
                                type: "dragstart",
                            });
                            this.helper !== this.el
                                ? (this._setupDragFollowNodeNotifyStart(e),
                                  this._dragFollow(t))
                                : (this.dragFollowTimer = window.setTimeout(
                                      () => {
                                          delete this.dragFollowTimer,
                                              this._setupDragFollowNodeNotifyStart(
                                                  e
                                              );
                                      },
                                      0
                                  )),
                                this._cancelDragGhost(t);
                        }
                        _setupDragFollowNodeNotifyStart(t) {
                            return (
                                this._setupHelperStyle(),
                                document.addEventListener(
                                    "dragover",
                                    this._drag,
                                    n.dragEventListenerOption
                                ),
                                this.dragEl.addEventListener(
                                    "dragend",
                                    this._dragEnd
                                ),
                                this.option.start &&
                                    this.option.start(t, this.ui()),
                                (this.dragging = !0),
                                this.helper.classList.add(
                                    "ui-draggable-dragging"
                                ),
                                this.triggerEvent("dragstart", t),
                                this
                            );
                        }
                        _drag(t) {
                            t.preventDefault(), this._dragFollow(t);
                            const e = o.DDUtils.initEvent(t, {
                                target: this.el,
                                type: "drag",
                            });
                            this.option.drag && this.option.drag(e, this.ui()),
                                this.triggerEvent("drag", e);
                        }
                        _dragEnd(t) {
                            if (this.dragFollowTimer)
                                return (
                                    clearTimeout(this.dragFollowTimer),
                                    void delete this.dragFollowTimer
                                );
                            this.paintTimer &&
                                cancelAnimationFrame(this.paintTimer),
                                document.removeEventListener(
                                    "dragover",
                                    this._drag,
                                    n.dragEventListenerOption
                                ),
                                this.dragEl.removeEventListener(
                                    "dragend",
                                    this._dragEnd
                                ),
                                (this.dragging = !1),
                                this.helper.classList.remove(
                                    "ui-draggable-dragging"
                                ),
                                (this.helperContainment.style.position =
                                    this.parentOriginStylePosition || null),
                                this.helper === this.el
                                    ? this._removeHelperStyle()
                                    : this.helper.remove();
                            const e = o.DDUtils.initEvent(t, {
                                target: this.el,
                                type: "dragstop",
                            });
                            this.option.stop && this.option.stop(e),
                                this.triggerEvent("dragstop", e),
                                delete s.DDManager.dragElement,
                                delete this.helper;
                        }
                        _createHelper(t) {
                            let e = this.el;
                            return (
                                typeof this.option.helper === "function"
                                    ? (e = this.option.helper(t))
                                    : this.option.helper === "clone" &&
                                      (e = o.DDUtils.clone(this.el)),
                                document.body.contains(e) ||
                                    o.DDUtils.appendTo(
                                        e,
                                        this.option.appendTo === "parent"
                                            ? this.el.parentNode
                                            : this.option.appendTo
                                    ),
                                e === this.el &&
                                    (this.dragElementOriginStyle =
                                        n.originStyleProp.map(
                                            (t) => this.el.style[t]
                                        )),
                                e
                            );
                        }
                        _setupHelperStyle() {
                            return (
                                (this.helper.style.pointerEvents = "none"),
                                (this.helper.style.width =
                                    this.dragOffset.width + "px"),
                                (this.helper.style.height =
                                    this.dragOffset.height + "px"),
                                (this.helper.style.willChange = "left, top"),
                                (this.helper.style.transition = "none"),
                                (this.helper.style.position =
                                    this.option.basePosition || n.basePosition),
                                (this.helper.style.zIndex = "1000"),
                                setTimeout(() => {
                                    this.helper &&
                                        (this.helper.style.transition = null);
                                }, 0),
                                this
                            );
                        }
                        _removeHelperStyle() {
                            const t = this.helper
                                ? this.helper.gridstackNode
                                : void 0;
                            return (
                                (t && t._isAboutToRemove) ||
                                    n.originStyleProp.forEach((t) => {
                                        this.helper.style[t] =
                                            this.dragElementOriginStyle[t] ||
                                            null;
                                    }),
                                delete this.dragElementOriginStyle,
                                this
                            );
                        }
                        _dragFollow(t) {
                            this.paintTimer &&
                                cancelAnimationFrame(this.paintTimer),
                                (this.paintTimer = requestAnimationFrame(() => {
                                    delete this.paintTimer;
                                    const e = this.dragOffset;
                                    let i = { left: 0, top: 0 };
                                    if (
                                        this.helper.style.position ===
                                        "absolute"
                                    ) {
                                        const { left: t, top: e } =
                                            this.helperContainment.getBoundingClientRect();
                                        i = { left: t, top: e };
                                    }
                                    (this.helper.style.left =
                                        t.clientX +
                                        e.offsetLeft -
                                        i.left +
                                        "px"),
                                        (this.helper.style.top =
                                            t.clientY +
                                            e.offsetTop -
                                            i.top +
                                            "px");
                                }));
                        }
                        _setupHelperContainmentStyle() {
                            return (
                                (this.helperContainment =
                                    this.helper.parentElement),
                                this.option.basePosition !== "fixed" &&
                                    ((this.parentOriginStylePosition =
                                        this.helperContainment.style.position),
                                    window
                                        .getComputedStyle(
                                            this.helperContainment
                                        )
                                        .position.match(/static/) &&
                                        (this.helperContainment.style.position =
                                            "relative")),
                                this
                            );
                        }
                        _cancelDragGhost(t) {
                            const e = document.createElement("div");
                            return (
                                (e.style.width = "1px"),
                                (e.style.height = "1px"),
                                (e.style.position = "fixed"),
                                document.body.appendChild(e),
                                t.dataTransfer.setDragImage(e, 0, 0),
                                setTimeout(() => document.body.removeChild(e)),
                                t.stopPropagation(),
                                this
                            );
                        }
                        _getDragOffset(t, e, i) {
                            let s = 0,
                                r = 0;
                            if (i) {
                                const t = document.createElement("div");
                                o.DDUtils.addElStyles(t, {
                                    opacity: "0",
                                    position: "fixed",
                                    top: "0px",
                                    left: "0px",
                                    width: "1px",
                                    height: "1px",
                                    zIndex: "-999999",
                                }),
                                    i.appendChild(t);
                                const e = t.getBoundingClientRect();
                                i.removeChild(t), (s = e.left), (r = e.top);
                            }
                            const n = e.getBoundingClientRect();
                            return {
                                left: n.left,
                                top: n.top,
                                offsetLeft: -t.clientX + n.left - s,
                                offsetTop: -t.clientY + n.top - r,
                                width: n.width,
                                height: n.height,
                            };
                        }
                    }
                    (e.DDDraggable = n),
                        (n.basePosition = "absolute"),
                        (n.dragEventListenerOption = !0),
                        (n.originStyleProp = [
                            "transition",
                            "pointerEvents",
                            "position",
                            "left",
                            "top",
                            "opacity",
                            "zIndex",
                            "width",
                            "height",
                            "willChange",
                        ]);
                },
                54: (t, e, i) => {
                    Object.defineProperty(e, "__esModule", { value: !0 }),
                        (e.DDDroppable = void 0);
                    const s = i(849),
                        o = i(861),
                        r = i(943);
                    class n extends o.DDBaseImplement {
                        constructor(t, e = {}) {
                            super(),
                                (this.el = t),
                                (this.option = e),
                                (this._dragEnter = this._dragEnter.bind(this)),
                                (this._dragOver = this._dragOver.bind(this)),
                                (this._dragLeave = this._dragLeave.bind(this)),
                                (this._drop = this._drop.bind(this)),
                                this.el.classList.add("ui-droppable"),
                                this.el.addEventListener(
                                    "dragenter",
                                    this._dragEnter
                                ),
                                this._setupAccept();
                        }
                        on(t, e) {
                            super.on(t, e);
                        }
                        off(t) {
                            super.off(t);
                        }
                        enable() {
                            this.disabled &&
                                (super.enable(),
                                this.el.classList.remove(
                                    "ui-droppable-disabled"
                                ),
                                this.el.addEventListener(
                                    "dragenter",
                                    this._dragEnter
                                ));
                        }
                        disable(t = !1) {
                            this.disabled ||
                                (super.disable(),
                                t ||
                                    this.el.classList.add(
                                        "ui-droppable-disabled"
                                    ),
                                this.el.removeEventListener(
                                    "dragenter",
                                    this._dragEnter
                                ));
                        }
                        destroy() {
                            this.moving && this._removeLeaveCallbacks(),
                                this.disable(!0),
                                this.el.classList.remove("ui-droppable"),
                                this.el.classList.remove(
                                    "ui-droppable-disabled"
                                ),
                                delete this.moving,
                                super.destroy();
                        }
                        updateOption(t) {
                            return (
                                Object.keys(t).forEach(
                                    (e) => (this.option[e] = t[e])
                                ),
                                this._setupAccept(),
                                this
                            );
                        }
                        _dragEnter(t) {
                            if (!this._canDrop()) return;
                            if ((t.preventDefault(), this.moving)) return;
                            this.moving = !0;
                            const e = r.DDUtils.initEvent(t, {
                                target: this.el,
                                type: "dropover",
                            });
                            this.option.over &&
                                this.option.over(
                                    e,
                                    this._ui(s.DDManager.dragElement)
                                ),
                                this.triggerEvent("dropover", e),
                                this.el.addEventListener(
                                    "dragover",
                                    this._dragOver
                                ),
                                this.el.addEventListener("drop", this._drop),
                                this.el.addEventListener(
                                    "dragleave",
                                    this._dragLeave
                                ),
                                this.el.classList.add("ui-droppable-over");
                        }
                        _dragOver(t) {
                            t.preventDefault(), t.stopPropagation();
                        }
                        _dragLeave(t) {
                            if (t.relatedTarget) {
                                if (this.el.contains(t.relatedTarget)) return;
                            } else {
                                const {
                                    bottom: e,
                                    left: i,
                                    right: s,
                                    top: o,
                                } = this.el.getBoundingClientRect();
                                if (t.x < s && t.x > i && t.y < e && t.y > o)
                                    return;
                            }
                            if ((this._removeLeaveCallbacks(), this.moving)) {
                                t.preventDefault();
                                const e = r.DDUtils.initEvent(t, {
                                    target: this.el,
                                    type: "dropout",
                                });
                                this.option.out &&
                                    this.option.out(
                                        e,
                                        this._ui(s.DDManager.dragElement)
                                    ),
                                    this.triggerEvent("dropout", e);
                            }
                            delete this.moving;
                        }
                        _drop(t) {
                            if (!this.moving) return;
                            t.preventDefault();
                            const e = r.DDUtils.initEvent(t, {
                                target: this.el,
                                type: "drop",
                            });
                            this.option.drop &&
                                this.option.drop(
                                    e,
                                    this._ui(s.DDManager.dragElement)
                                ),
                                this.triggerEvent("drop", e),
                                this._removeLeaveCallbacks(),
                                delete this.moving;
                        }
                        _removeLeaveCallbacks() {
                            this.el.removeEventListener(
                                "dragleave",
                                this._dragLeave
                            ),
                                this.el.classList.remove("ui-droppable-over"),
                                this.moving &&
                                    (this.el.removeEventListener(
                                        "dragover",
                                        this._dragOver
                                    ),
                                    this.el.removeEventListener(
                                        "drop",
                                        this._drop
                                    ));
                        }
                        _canDrop() {
                            return (
                                s.DDManager.dragElement &&
                                (!this.accept ||
                                    this.accept(s.DDManager.dragElement.el))
                            );
                        }
                        _setupAccept() {
                            return (
                                this.option.accept &&
                                typeof this.option.accept === "string"
                                    ? (this.accept = (t) =>
                                          t.matches(this.option.accept))
                                    : (this.accept = this.option.accept),
                                this
                            );
                        }
                        _ui(t) {
                            return Object.assign({ draggable: t.el }, t.ui());
                        }
                    }
                    e.DDDroppable = n;
                },
                485: (t, e, i) => {
                    Object.defineProperty(e, "__esModule", { value: !0 }),
                        (e.DDElement = void 0);
                    const s = i(97),
                        o = i(311),
                        r = i(54);
                    class n {
                        constructor(t) {
                            this.el = t;
                        }
                        static init(t) {
                            return (
                                t.ddElement || (t.ddElement = new n(t)),
                                t.ddElement
                            );
                        }
                        on(t, e) {
                            return (
                                this.ddDraggable &&
                                ["drag", "dragstart", "dragstop"].indexOf(t) >
                                    -1
                                    ? this.ddDraggable.on(t, e)
                                    : this.ddDroppable &&
                                      ["drop", "dropover", "dropout"].indexOf(
                                          t
                                      ) > -1
                                    ? this.ddDroppable.on(t, e)
                                    : this.ddResizable &&
                                      [
                                          "resizestart",
                                          "resize",
                                          "resizestop",
                                      ].indexOf(t) > -1 &&
                                      this.ddResizable.on(t, e),
                                this
                            );
                        }
                        off(t) {
                            return (
                                this.ddDraggable &&
                                ["drag", "dragstart", "dragstop"].indexOf(t) >
                                    -1
                                    ? this.ddDraggable.off(t)
                                    : this.ddDroppable &&
                                      ["drop", "dropover", "dropout"].indexOf(
                                          t
                                      ) > -1
                                    ? this.ddDroppable.off(t)
                                    : this.ddResizable &&
                                      [
                                          "resizestart",
                                          "resize",
                                          "resizestop",
                                      ].indexOf(t) > -1 &&
                                      this.ddResizable.off(t),
                                this
                            );
                        }
                        setupDraggable(t) {
                            return (
                                this.ddDraggable
                                    ? this.ddDraggable.updateOption(t)
                                    : (this.ddDraggable = new o.DDDraggable(
                                          this.el,
                                          t
                                      )),
                                this
                            );
                        }
                        cleanDraggable() {
                            return (
                                this.ddDraggable &&
                                    (this.ddDraggable.destroy(),
                                    delete this.ddDraggable),
                                this
                            );
                        }
                        setupResizable(t) {
                            return (
                                this.ddResizable
                                    ? this.ddResizable.updateOption(t)
                                    : (this.ddResizable = new s.DDResizable(
                                          this.el,
                                          t
                                      )),
                                this
                            );
                        }
                        cleanResizable() {
                            return (
                                this.ddResizable &&
                                    (this.ddResizable.destroy(),
                                    delete this.ddResizable),
                                this
                            );
                        }
                        setupDroppable(t) {
                            return (
                                this.ddDroppable
                                    ? this.ddDroppable.updateOption(t)
                                    : (this.ddDroppable = new r.DDDroppable(
                                          this.el,
                                          t
                                      )),
                                this
                            );
                        }
                        cleanDroppable() {
                            return (
                                this.ddDroppable &&
                                    (this.ddDroppable.destroy(),
                                    delete this.ddDroppable),
                                this
                            );
                        }
                    }
                    e.DDElement = n;
                },
                849: (t, e) => {
                    Object.defineProperty(e, "__esModule", { value: !0 }),
                        (e.DDManager = void 0),
                        (e.DDManager = class {});
                },
                680: (t, e) => {
                    Object.defineProperty(e, "__esModule", { value: !0 }),
                        (e.DDResizableHandle = void 0);
                    class i {
                        constructor(t, e, i) {
                            (this.moving = !1),
                                (this.host = t),
                                (this.dir = e),
                                (this.option = i),
                                (this._mouseDown = this._mouseDown.bind(this)),
                                (this._mouseMove = this._mouseMove.bind(this)),
                                (this._mouseUp = this._mouseUp.bind(this)),
                                this._init();
                        }
                        _init() {
                            const t = document.createElement("div");
                            return (
                                t.classList.add("ui-resizable-handle"),
                                t.classList.add(`${i.prefix}${this.dir}`),
                                (t.style.zIndex = "100"),
                                (t.style.userSelect = "none"),
                                (this.el = t),
                                this.host.appendChild(this.el),
                                this.el.addEventListener(
                                    "mousedown",
                                    this._mouseDown
                                ),
                                this
                            );
                        }
                        destroy() {
                            return (
                                this.moving &&
                                    this._mouseUp(this.mouseDownEvent),
                                this.el.removeEventListener(
                                    "mousedown",
                                    this._mouseDown
                                ),
                                this.host.removeChild(this.el),
                                delete this.el,
                                delete this.host,
                                this
                            );
                        }
                        _mouseDown(t) {
                            t.preventDefault(),
                                (this.mouseDownEvent = t),
                                document.addEventListener(
                                    "mousemove",
                                    this._mouseMove,
                                    !0
                                ),
                                document.addEventListener(
                                    "mouseup",
                                    this._mouseUp
                                );
                        }
                        _mouseMove(t) {
                            const e = this.mouseDownEvent;
                            !this.moving &&
                            Math.abs(t.x - e.x) + Math.abs(t.y - e.y) > 2
                                ? ((this.moving = !0),
                                  this._triggerEvent(
                                      "start",
                                      this.mouseDownEvent
                                  ))
                                : this.moving && this._triggerEvent("move", t);
                        }
                        _mouseUp(t) {
                            this.moving && this._triggerEvent("stop", t),
                                document.removeEventListener(
                                    "mousemove",
                                    this._mouseMove,
                                    !0
                                ),
                                document.removeEventListener(
                                    "mouseup",
                                    this._mouseUp
                                ),
                                delete this.moving,
                                delete this.mouseDownEvent;
                        }
                        _triggerEvent(t, e) {
                            return this.option[t] && this.option[t](e), this;
                        }
                    }
                    (e.DDResizableHandle = i), (i.prefix = "ui-resizable-");
                },
                97: (t, e, i) => {
                    Object.defineProperty(e, "__esModule", { value: !0 }),
                        (e.DDResizable = void 0);
                    const s = i(680),
                        o = i(861),
                        r = i(943),
                        n = i(593);
                    class l extends o.DDBaseImplement {
                        constructor(t, e = {}) {
                            super(),
                                (this._showHandlers = () => {
                                    this.el.classList.remove(
                                        "ui-resizable-autohide"
                                    );
                                }),
                                (this._hideHandlers = () => {
                                    this.el.classList.add(
                                        "ui-resizable-autohide"
                                    );
                                }),
                                (this._ui = () => {
                                    const t =
                                            this.el.parentElement.getBoundingClientRect(),
                                        e = {
                                            width: this.originalRect.width,
                                            height:
                                                this.originalRect.height +
                                                this.scrolled,
                                            left: this.originalRect.left,
                                            top:
                                                this.originalRect.top -
                                                this.scrolled,
                                        },
                                        i = this.temporalRect || e;
                                    return {
                                        position: {
                                            left: i.left - t.left,
                                            top: i.top - t.top,
                                        },
                                        size: {
                                            width: i.width,
                                            height: i.height,
                                        },
                                    };
                                }),
                                (this.el = t),
                                (this.option = e),
                                this.enable(),
                                this._setupAutoHide(),
                                this._setupHandlers();
                        }
                        on(t, e) {
                            super.on(t, e);
                        }
                        off(t) {
                            super.off(t);
                        }
                        enable() {
                            super.enable(),
                                this.el.classList.add("ui-resizable"),
                                this.el.classList.remove(
                                    "ui-resizable-disabled"
                                );
                        }
                        disable() {
                            super.disable(),
                                this.el.classList.add("ui-resizable-disabled"),
                                this.el.classList.remove("ui-resizable");
                        }
                        destroy() {
                            this._removeHandlers(),
                                this.option.autoHide &&
                                    (this.el.removeEventListener(
                                        "mouseover",
                                        this._showHandlers
                                    ),
                                    this.el.removeEventListener(
                                        "mouseout",
                                        this._hideHandlers
                                    )),
                                this.el.classList.remove("ui-resizable"),
                                delete this.el,
                                super.destroy();
                        }
                        updateOption(t) {
                            const e =
                                    t.handles &&
                                    t.handles !== this.option.handles,
                                i =
                                    t.autoHide &&
                                    t.autoHide !== this.option.autoHide;
                            return (
                                Object.keys(t).forEach(
                                    (e) => (this.option[e] = t[e])
                                ),
                                e &&
                                    (this._removeHandlers(),
                                    this._setupHandlers()),
                                i && this._setupAutoHide(),
                                this
                            );
                        }
                        _setupAutoHide() {
                            return (
                                this.option.autoHide
                                    ? (this.el.classList.add(
                                          "ui-resizable-autohide"
                                      ),
                                      this.el.addEventListener(
                                          "mouseover",
                                          this._showHandlers
                                      ),
                                      this.el.addEventListener(
                                          "mouseout",
                                          this._hideHandlers
                                      ))
                                    : (this.el.classList.remove(
                                          "ui-resizable-autohide"
                                      ),
                                      this.el.removeEventListener(
                                          "mouseover",
                                          this._showHandlers
                                      ),
                                      this.el.removeEventListener(
                                          "mouseout",
                                          this._hideHandlers
                                      )),
                                this
                            );
                        }
                        _setupHandlers() {
                            let t = this.option.handles || "e,s,se";
                            return (
                                t === "all" && (t = "n,e,s,w,se,sw,ne,nw"),
                                (this.handlers = t
                                    .split(",")
                                    .map((t) => t.trim())
                                    .map(
                                        (t) =>
                                            new s.DDResizableHandle(
                                                this.el,
                                                t,
                                                {
                                                    start: (t) => {
                                                        this._resizeStart(t);
                                                    },
                                                    stop: (t) => {
                                                        this._resizeStop(t);
                                                    },
                                                    move: (e) => {
                                                        this._resizing(e, t);
                                                    },
                                                }
                                            )
                                    )),
                                this
                            );
                        }
                        _resizeStart(t) {
                            (this.originalRect =
                                this.el.getBoundingClientRect()),
                                (this.scrollEl = n.Utils.getScrollElement(
                                    this.el
                                )),
                                (this.scrollY = this.scrollEl.scrollTop),
                                (this.scrolled = 0),
                                (this.startEvent = t),
                                this._setupHelper(),
                                this._applyChange();
                            const e = r.DDUtils.initEvent(t, {
                                type: "resizestart",
                                target: this.el,
                            });
                            return (
                                this.option.start &&
                                    this.option.start(e, this._ui()),
                                this.el.classList.add("ui-resizable-resizing"),
                                this.triggerEvent("resizestart", e),
                                this
                            );
                        }
                        _resizing(t, e) {
                            (this.scrolled =
                                this.scrollEl.scrollTop - this.scrollY),
                                (this.temporalRect = this._getChange(t, e)),
                                this._applyChange();
                            const i = r.DDUtils.initEvent(t, {
                                type: "resize",
                                target: this.el,
                            });
                            return (
                                this.option.resize &&
                                    this.option.resize(i, this._ui()),
                                this.triggerEvent("resize", i),
                                this
                            );
                        }
                        _resizeStop(t) {
                            const e = r.DDUtils.initEvent(t, {
                                type: "resizestop",
                                target: this.el,
                            });
                            return (
                                this.option.stop && this.option.stop(e),
                                this.el.classList.remove(
                                    "ui-resizable-resizing"
                                ),
                                this.triggerEvent("resizestop", e),
                                this._cleanHelper(),
                                delete this.startEvent,
                                delete this.originalRect,
                                delete this.temporalRect,
                                delete this.scrollY,
                                delete this.scrolled,
                                this
                            );
                        }
                        _setupHelper() {
                            return (
                                (this.elOriginStyleVal = l._originStyleProp.map(
                                    (t) => this.el.style[t]
                                )),
                                (this.parentOriginStylePosition =
                                    this.el.parentElement.style.position),
                                window
                                    .getComputedStyle(this.el.parentElement)
                                    .position.match(/static/) &&
                                    (this.el.parentElement.style.position =
                                        "relative"),
                                (this.el.style.position =
                                    this.option.basePosition || "absolute"),
                                (this.el.style.opacity = "0.8"),
                                (this.el.style.zIndex = "1000"),
                                this
                            );
                        }
                        _cleanHelper() {
                            return (
                                l._originStyleProp.forEach((t, e) => {
                                    this.el.style[t] =
                                        this.elOriginStyleVal[e] || null;
                                }),
                                (this.el.parentElement.style.position =
                                    this.parentOriginStylePosition || null),
                                this
                            );
                        }
                        _getChange(t, e) {
                            const i = this.startEvent,
                                s = {
                                    width: this.originalRect.width,
                                    height:
                                        this.originalRect.height +
                                        this.scrolled,
                                    left: this.originalRect.left,
                                    top: this.originalRect.top - this.scrolled,
                                },
                                o = t.clientX - i.clientX,
                                r = t.clientY - i.clientY;
                            e.indexOf("e") > -1
                                ? (s.width += o)
                                : e.indexOf("w") > -1 &&
                                  ((s.width -= o), (s.left += o)),
                                e.indexOf("s") > -1
                                    ? (s.height += r)
                                    : e.indexOf("n") > -1 &&
                                      ((s.height -= r), (s.top += r));
                            const n = this._constrainSize(s.width, s.height);
                            return (
                                Math.round(s.width) !== Math.round(n.width) &&
                                    (e.indexOf("w") > -1 &&
                                        (s.left += s.width - n.width),
                                    (s.width = n.width)),
                                Math.round(s.height) !== Math.round(n.height) &&
                                    (e.indexOf("n") > -1 &&
                                        (s.top += s.height - n.height),
                                    (s.height = n.height)),
                                s
                            );
                        }
                        _constrainSize(t, e) {
                            const i =
                                    this.option.maxWidth ||
                                    Number.MAX_SAFE_INTEGER,
                                s = this.option.minWidth || t,
                                o =
                                    this.option.maxHeight ||
                                    Number.MAX_SAFE_INTEGER,
                                r = this.option.minHeight || e;
                            return {
                                width: Math.min(i, Math.max(s, t)),
                                height: Math.min(o, Math.max(r, e)),
                            };
                        }
                        _applyChange() {
                            let t = { left: 0, top: 0, width: 0, height: 0 };
                            if (this.el.style.position === "absolute") {
                                const e = this.el.parentElement,
                                    { left: i, top: s } =
                                        e.getBoundingClientRect();
                                t = { left: i, top: s, width: 0, height: 0 };
                            }
                            return this.temporalRect
                                ? (Object.keys(this.temporalRect).forEach(
                                      (e) => {
                                          const i = this.temporalRect[e];
                                          this.el.style[e] = i - t[e] + "px";
                                      }
                                  ),
                                  this)
                                : this;
                        }
                        _removeHandlers() {
                            return (
                                this.handlers.forEach((t) => t.destroy()),
                                delete this.handlers,
                                this
                            );
                        }
                    }
                    (e.DDResizable = l),
                        (l._originStyleProp = [
                            "width",
                            "height",
                            "position",
                            "left",
                            "top",
                            "opacity",
                            "zIndex",
                        ]);
                },
                943: (t, e) => {
                    Object.defineProperty(e, "__esModule", { value: !0 }),
                        (e.DDUtils = void 0);
                    class i {
                        static clone(t) {
                            const e = t.cloneNode(!0);
                            return e.removeAttribute("id"), e;
                        }
                        static appendTo(t, e) {
                            let i;
                            (i =
                                typeof e === "string"
                                    ? document.querySelector(e)
                                    : e),
                                i && i.appendChild(t);
                        }
                        static setPositionRelative(t) {
                            /^(?:r|a|f)/.test(
                                window.getComputedStyle(t).position
                            ) || (t.style.position = "relative");
                        }
                        static addElStyles(t, e) {
                            if (e instanceof Object)
                                for (const i in e)
                                    e.hasOwnProperty(i) &&
                                        (Array.isArray(e[i])
                                            ? e[i].forEach((e) => {
                                                  t.style[i] = e;
                                              })
                                            : (t.style[i] = e[i]));
                        }
                        static initEvent(t, e) {
                            const i = { type: e.type },
                                s = {
                                    button: 0,
                                    which: 0,
                                    buttons: 1,
                                    bubbles: !0,
                                    cancelable: !0,
                                    target: e.target ? e.target : t.target,
                                };
                            return (
                                t.dataTransfer &&
                                    (i.dataTransfer = t.dataTransfer),
                                [
                                    "altKey",
                                    "ctrlKey",
                                    "metaKey",
                                    "shiftKey",
                                ].forEach((e) => (i[e] = t[e])),
                                [
                                    "pageX",
                                    "pageY",
                                    "clientX",
                                    "clientY",
                                    "screenX",
                                    "screenY",
                                ].forEach((e) => (i[e] = t[e])),
                                Object.assign(Object.assign({}, i), s)
                            );
                        }
                    }
                    (e.DDUtils = i),
                        (i.isEventSupportPassiveOption = (() => {
                            let t = !1,
                                e = () => {};
                            return (
                                document.addEventListener("test", e, {
                                    get passive() {
                                        return (t = !0), !0;
                                    },
                                }),
                                document.removeEventListener("test", e),
                                t
                            );
                        })());
                },
                761: function (t, e, i) {
                    var s =
                            (this && this.__createBinding) ||
                            (Object.create
                                ? function (t, e, i, s) {
                                      void 0 === s && (s = i),
                                          Object.defineProperty(t, s, {
                                              enumerable: !0,
                                              get: function () {
                                                  return e[i];
                                              },
                                          });
                                  }
                                : function (t, e, i, s) {
                                      void 0 === s && (s = i), (t[s] = e[i]);
                                  }),
                        o =
                            (this && this.__exportStar) ||
                            function (t, e) {
                                for (var i in t)
                                    i === "default" ||
                                        e.hasOwnProperty(i) ||
                                        s(e, t, i);
                            };
                    Object.defineProperty(e, "__esModule", { value: !0 }),
                        (e.GridStackDDNative = void 0);
                    const r = i(849),
                        n = i(485),
                        l = i(21),
                        a = i(593);
                    o(i(21), e);
                    class h extends l.GridStackDD {
                        resizable(t, e, i, s) {
                            return (
                                this._getDDElements(t).forEach((t) => {
                                    if (e === "disable" || e === "enable")
                                        t.ddResizable && t.ddResizable[e]();
                                    else if (e === "destroy")
                                        t.ddResizable && t.cleanResizable();
                                    else if (e === "option")
                                        t.setupResizable({ [i]: s });
                                    else {
                                        const i = t.el.gridstackNode.grid;
                                        const s = t.el.getAttribute(
                                            "gs-resize-handles"
                                        )
                                            ? t.el.getAttribute(
                                                  "gs-resize-handles"
                                              )
                                            : i.opts.resizable.handles;
                                        t.setupResizable(
                                            Object.assign(
                                                Object.assign(
                                                    Object.assign(
                                                        {},
                                                        i.opts.resizable
                                                    ),
                                                    { handles: s }
                                                ),
                                                {
                                                    start: e.start,
                                                    stop: e.stop,
                                                    resize: e.resize,
                                                }
                                            )
                                        );
                                    }
                                }),
                                this
                            );
                        }
                        draggable(t, e, i, s) {
                            return (
                                this._getDDElements(t).forEach((t) => {
                                    if (e === "disable" || e === "enable")
                                        t.ddDraggable && t.ddDraggable[e]();
                                    else if (e === "destroy")
                                        t.ddDraggable && t.cleanDraggable();
                                    else if (e === "option")
                                        t.setupDraggable({ [i]: s });
                                    else {
                                        const i = t.el.gridstackNode.grid;
                                        t.setupDraggable(
                                            Object.assign(
                                                Object.assign(
                                                    {},
                                                    i.opts.draggable
                                                ),
                                                {
                                                    containment:
                                                        i.opts._isNested &&
                                                        !i.opts.dragOut
                                                            ? i.el.parentElement
                                                            : i.opts.draggable
                                                                  .containment ||
                                                              null,
                                                    start: e.start,
                                                    stop: e.stop,
                                                    drag: e.drag,
                                                }
                                            )
                                        );
                                    }
                                }),
                                this
                            );
                        }
                        dragIn(t, e) {
                            return (
                                this._getDDElements(t).forEach((t) =>
                                    t.setupDraggable(e)
                                ),
                                this
                            );
                        }
                        droppable(t, e, i, s) {
                            return (
                                typeof e.accept !== "function" ||
                                    e._accept ||
                                    ((e._accept = e.accept),
                                    (e.accept = (t) => e._accept(t))),
                                this._getDDElements(t).forEach((t) => {
                                    e === "disable" || e === "enable"
                                        ? t.ddDroppable && t.ddDroppable[e]()
                                        : e === "destroy"
                                        ? t.ddDroppable && t.cleanDroppable()
                                        : e === "option"
                                        ? t.setupDroppable({ [i]: s })
                                        : t.setupDroppable(e);
                                }),
                                this
                            );
                        }
                        isDroppable(t) {
                            return !(
                                !(
                                    t &&
                                    t.ddElement &&
                                    t.ddElement.ddDroppable
                                ) || t.ddElement.ddDroppable.disabled
                            );
                        }
                        isDraggable(t) {
                            return !(
                                !(
                                    t &&
                                    t.ddElement &&
                                    t.ddElement.ddDraggable
                                ) || t.ddElement.ddDraggable.disabled
                            );
                        }
                        isResizable(t) {
                            return !(
                                !(
                                    t &&
                                    t.ddElement &&
                                    t.ddElement.ddResizable
                                ) || t.ddElement.ddResizable.disabled
                            );
                        }
                        on(t, e, i) {
                            return (
                                this._getDDElements(t).forEach((t) =>
                                    t.on(e, (t) => {
                                        i(
                                            t,
                                            r.DDManager.dragElement
                                                ? r.DDManager.dragElement.el
                                                : t.target,
                                            r.DDManager.dragElement
                                                ? r.DDManager.dragElement.helper
                                                : null
                                        );
                                    })
                                ),
                                this
                            );
                        }
                        off(t, e) {
                            return (
                                this._getDDElements(t).forEach((t) => t.off(e)),
                                this
                            );
                        }
                        _getDDElements(t, e = !0) {
                            const i = a.Utils.getElements(t);
                            if (!i.length) return [];
                            const s = i.map(
                                (t) =>
                                    t.ddElement ||
                                    (e ? n.DDElement.init(t) : null)
                            );
                            return e || s.filter((t) => t), s;
                        }
                    }
                    (e.GridStackDDNative = h), l.GridStackDD.registerPlugin(h);
                },
                699: (t, e) => {
                    Object.defineProperty(e, "__esModule", { value: !0 });
                },
                593: (t, e) => {
                    Object.defineProperty(e, "__esModule", { value: !0 }),
                        (e.Utils =
                            e.obsoleteAttr =
                            e.obsoleteOptsDel =
                            e.obsoleteOpts =
                            e.obsolete =
                                void 0),
                        (e.obsolete = function (t, e, i, s, o) {
                            const r = (...r) => (
                                console.warn(
                                    "gridstack.js: Function `" +
                                        i +
                                        "` is deprecated in " +
                                        o +
                                        " and has been replaced with `" +
                                        s +
                                        "`. It will be **completely** removed in v1.0"
                                ),
                                e.apply(t, r)
                            );
                            return (r.prototype = e.prototype), r;
                        }),
                        (e.obsoleteOpts = function (t, e, i, s) {
                            void 0 !== t[e] &&
                                ((t[i] = t[e]),
                                console.warn(
                                    "gridstack.js: Option `" +
                                        e +
                                        "` is deprecated in " +
                                        s +
                                        " and has been replaced with `" +
                                        i +
                                        "`. It will be **completely** removed in v1.0"
                                ));
                        }),
                        (e.obsoleteOptsDel = function (t, e, i, s) {
                            void 0 !== t[e] &&
                                console.warn(
                                    "gridstack.js: Option `" +
                                        e +
                                        "` is deprecated in " +
                                        i +
                                        s
                                );
                        }),
                        (e.obsoleteAttr = function (t, e, i, s) {
                            const o = t.getAttribute(e);
                            o !== null &&
                                (t.setAttribute(i, o),
                                console.warn(
                                    "gridstack.js: attribute `" +
                                        e +
                                        "`=" +
                                        o +
                                        " is deprecated on this object in " +
                                        s +
                                        " and has been replaced with `" +
                                        i +
                                        "`. It will be **completely** removed in v1.0"
                                ));
                        });
                    class i {
                        static getElements(t) {
                            if (typeof t === "string") {
                                let e = document.querySelectorAll(t);
                                return (
                                    e.length ||
                                        t[0] === "." ||
                                        t[0] === "#" ||
                                        ((e = document.querySelectorAll(
                                            "." + t
                                        )),
                                        e.length ||
                                            (e = document.querySelectorAll(
                                                "#" + t
                                            ))),
                                    Array.from(e)
                                );
                            }
                            return [t];
                        }
                        static getElement(t) {
                            if (typeof t === "string") {
                                if (!t.length) return null;
                                if (t[0] === "#")
                                    return document.getElementById(
                                        t.substring(1)
                                    );
                                if (t[0] === "." || t[0] === "[")
                                    return document.querySelector(t);
                                if (!isNaN(Number(t[0])))
                                    return document.getElementById(t);
                                let e = document.querySelector(t);
                                return (
                                    e || (e = document.getElementById(t)),
                                    e || (e = document.querySelector("." + t)),
                                    e
                                );
                            }
                            return t;
                        }
                        static isIntercepted(t, e) {
                            return !(
                                t.y >= e.y + e.h ||
                                t.y + t.h <= e.y ||
                                t.x + t.w <= e.x ||
                                t.x >= e.x + e.w
                            );
                        }
                        static isTouching(t, e) {
                            return i.isIntercepted(t, {
                                x: e.x - 0.5,
                                y: e.y - 0.5,
                                w: e.w + 1,
                                h: e.h + 1,
                            });
                        }
                        static sort(t, e, i) {
                            return (
                                (i =
                                    i ||
                                    t.reduce(
                                        (t, e) => Math.max(e.x + e.w, t),
                                        0
                                    ) ||
                                    12),
                                e === -1
                                    ? t.sort(
                                          (t, e) =>
                                              e.x + e.y * i - (t.x + t.y * i)
                                      )
                                    : t.sort(
                                          (t, e) =>
                                              t.x + t.y * i - (e.x + e.y * i)
                                      )
                            );
                        }
                        static createStylesheet(t, e) {
                            const i = document.createElement("style");
                            return (
                                i.setAttribute("type", "text/css"),
                                i.setAttribute("gs-style-id", t),
                                i.styleSheet
                                    ? (i.styleSheet.cssText = "")
                                    : i.appendChild(
                                          document.createTextNode("")
                                      ),
                                e
                                    ? e.insertBefore(i, e.firstChild)
                                    : (e =
                                          document.getElementsByTagName(
                                              "head"
                                          )[0]).appendChild(i),
                                i.sheet
                            );
                        }
                        static removeStylesheet(t) {
                            const e = document.querySelector(
                                "STYLE[gs-style-id=" + t + "]"
                            );
                            e && e.parentNode && e.remove();
                        }
                        static addCSSRule(t, e, i) {
                            typeof t.addRule === "function"
                                ? t.addRule(e, i)
                                : typeof t.insertRule === "function" &&
                                  t.insertRule(`${e}{${i}}`);
                        }
                        static toBool(t) {
                            return typeof t === "boolean"
                                ? t
                                : typeof t === "string"
                                ? !(
                                      (t = t.toLowerCase()) === "" ||
                                      t === "no" ||
                                      t === "false" ||
                                      t === "0"
                                  )
                                : Boolean(t);
                        }
                        static toNumber(t) {
                            return t === null || t.length === 0
                                ? void 0
                                : Number(t);
                        }
                        static parseHeight(t) {
                            let e,
                                i = "px";
                            if (typeof t === "string") {
                                const s = t.match(
                                    /^(-[0-9]+\.[0-9]+|[0-9]*\.[0-9]+|-[0-9]+|[0-9]+)(px|em|rem|vh|vw|%)?$/
                                );
                                if (!s) throw new Error("Invalid height");
                                (i = s[2] || "px"), (e = parseFloat(s[1]));
                            } else e = t;
                            return { h: e, unit: i };
                        }
                        static defaults(t, ...e) {
                            return (
                                e.forEach((e) => {
                                    for (const i in e) {
                                        if (!e.hasOwnProperty(i)) return;
                                        t[i] === null || void 0 === t[i]
                                            ? (t[i] = e[i])
                                            : typeof e[i] === "object" &&
                                              typeof t[i] === "object" &&
                                              this.defaults(t[i], e[i]);
                                    }
                                }),
                                t
                            );
                        }
                        static same(t, e) {
                            if (typeof t !== "object") return t == e;
                            if (typeof t !== typeof e) return !1;
                            if (Object.keys(t).length !== Object.keys(e).length)
                                return !1;
                            for (const i in t) if (t[i] !== e[i]) return !1;
                            return !0;
                        }
                        static copyPos(t, e, i = !1) {
                            return (
                                (t.x = e.x),
                                (t.y = e.y),
                                (t.w = e.w),
                                (t.h = e.h),
                                i
                                    ? (e.minW && (t.minW = e.minW),
                                      e.minH && (t.minH = e.minH),
                                      e.maxW && (t.maxW = e.maxW),
                                      e.maxH && (t.maxH = e.maxH),
                                      t)
                                    : t
                            );
                        }
                        static samePos(t, e) {
                            return (
                                t &&
                                e &&
                                t.x === e.x &&
                                t.y === e.y &&
                                t.w === e.w &&
                                t.h === e.h
                            );
                        }
                        static removeInternalAndSame(t, e) {
                            if (typeof t === "object" && typeof e === "object")
                                for (const i in t) {
                                    const s = t[i];
                                    if (i[0] === "_" || s === e[i]) delete t[i];
                                    else if (
                                        s &&
                                        typeof s === "object" &&
                                        void 0 !== e[i]
                                    ) {
                                        for (const t in s)
                                            (s[t] !== e[i][t] &&
                                                t[0] !== "_") ||
                                                delete s[t];
                                        Object.keys(s).length || delete t[i];
                                    }
                                }
                        }
                        static closestByClass(t, e) {
                            for (; (t = t.parentElement); )
                                if (t.classList.contains(e)) return t;
                            return null;
                        }
                        static throttle(t, e) {
                            let i = !1;
                            return (...s) => {
                                i ||
                                    ((i = !0),
                                    setTimeout(() => {
                                        t(...s), (i = !1);
                                    }, e));
                            };
                        }
                        static removePositioningStyles(t) {
                            const e = t.style;
                            e.position && e.removeProperty("position"),
                                e.left && e.removeProperty("left"),
                                e.top && e.removeProperty("top"),
                                e.width && e.removeProperty("width"),
                                e.height && e.removeProperty("height");
                        }
                        static getScrollElement(t) {
                            if (!t)
                                return (
                                    document.scrollingElement ||
                                    document.documentElement
                                );
                            const e = getComputedStyle(t);
                            return /(auto|scroll)/.test(
                                e.overflow + e.overflowY
                            )
                                ? t
                                : this.getScrollElement(t.parentElement);
                        }
                        static updateScrollPosition(t, e, i) {
                            const s = t.getBoundingClientRect(),
                                o =
                                    window.innerHeight ||
                                    document.documentElement.clientHeight;
                            if (s.top < 0 || s.bottom > o) {
                                const r = s.bottom - o,
                                    n = s.top,
                                    l = this.getScrollElement(t);
                                if (l !== null) {
                                    const a = l.scrollTop;
                                    s.top < 0 && i < 0
                                        ? t.offsetHeight > o
                                            ? (l.scrollTop += i)
                                            : (l.scrollTop +=
                                                  Math.abs(n) > Math.abs(i)
                                                      ? i
                                                      : n)
                                        : i > 0 &&
                                          (t.offsetHeight > o
                                              ? (l.scrollTop += i)
                                              : (l.scrollTop += r > i ? i : r)),
                                        (e.top += l.scrollTop - a);
                                }
                            }
                        }
                        static updateScrollResize(t, e, i) {
                            const s = this.getScrollElement(e),
                                o = s.clientHeight,
                                r =
                                    s === this.getScrollElement()
                                        ? 0
                                        : s.getBoundingClientRect().top,
                                n = t.clientY - r,
                                l = n > o - i;
                            n < i
                                ? s.scrollBy({ behavior: "smooth", top: n - i })
                                : l &&
                                  s.scrollBy({
                                      behavior: "smooth",
                                      top: i - (o - n),
                                  });
                        }
                        static clone(t) {
                            return t == null || typeof t !== "object"
                                ? t
                                : t instanceof Array
                                ? [...t]
                                : Object.assign({}, t);
                        }
                        static cloneDeep(t) {
                            const e = i.clone(t);
                            for (const o in e)
                                e.hasOwnProperty(o) &&
                                    typeof e[o] === "object" &&
                                    o.substring(0, 2) !== "__" &&
                                    !s.find((t) => t === o) &&
                                    (e[o] = i.cloneDeep(t[o]));
                            return e;
                        }
                    }
                    e.Utils = i;
                    const s = ["_isNested", "el", "grid", "subGrid", "engine"];
                },
            },
            e = {},
            i = (function i(s) {
                var o = e[s];
                if (void 0 !== o) return o.exports;
                var r = (e[s] = { exports: {} });
                return t[s].call(r.exports, r, r.exports, i), r.exports;
            })(930);
        return i.GridStack;
    })();
});
