/* !
 * chartjs-plugin-datalabels v0.6.0
 * https://chartjs-plugin-datalabels.netlify.com
 * (c) 2019 Chart.js Contributors
 * Released under the MIT license
 */
!(function (t, e) {
    typeof exports === "object" && typeof module !== "undefined"
        ? (module.exports = e(require("chart.js")))
        : typeof define === "function" && define.amd
        ? define(["chart.js"], e)
        : ((t = t || self).ChartDataLabels = e(t.Chart));
})(this, function (t) {
    "use strict";
    var e = (t = t && t.hasOwnProperty("default") ? t.default : t).helpers,
        r = (function () {
            if (typeof window !== "undefined") {
                if (window.devicePixelRatio) return window.devicePixelRatio;
                var t = window.screen;
                if (t) return (t.deviceXDPI || 1) / (t.logicalXDPI || 1);
            }
            return 1;
        })(),
        n = {
            toTextLines: function (t) {
                var r,
                    n = [];
                for (t = [].concat(t); t.length; )
                    typeof (r = t.pop()) === "string"
                        ? n.unshift.apply(n, r.split("\n"))
                        : Array.isArray(r)
                        ? t.push.apply(t, r)
                        : e.isNullOrUndef(t) || n.unshift(String(r));
                return n;
            },
            toFontString: function (t) {
                return !t ||
                    e.isNullOrUndef(t.size) ||
                    e.isNullOrUndef(t.family)
                    ? null
                    : (t.style ? t.style + " " : "") +
                          (t.weight ? t.weight + " " : "") +
                          t.size +
                          "px " +
                          t.family;
            },
            textSize: function (t, e, r) {
                var n,
                    i = [].concat(e),
                    a = i.length,
                    o = t.font,
                    l = 0;
                for (t.font = r.string, n = 0; n < a; ++n)
                    l = Math.max(t.measureText(i[n]).width, l);
                return (t.font = o), { height: a * r.lineHeight, width: l };
            },
            parseFont: function (r) {
                var i = t.defaults.global,
                    a = e.valueOrDefault(r.size, i.defaultFontSize),
                    o = {
                        family: e.valueOrDefault(r.family, i.defaultFontFamily),
                        lineHeight: e.options.toLineHeight(r.lineHeight, a),
                        size: a,
                        style: e.valueOrDefault(r.style, i.defaultFontStyle),
                        weight: e.valueOrDefault(r.weight, null),
                        string: "",
                    };
                return (o.string = n.toFontString(o)), o;
            },
            bound: function (t, e, r) {
                return Math.max(t, Math.min(e, r));
            },
            arrayDiff: function (t, e) {
                var r,
                    n,
                    i,
                    a,
                    o = t.slice(),
                    l = [];
                for (r = 0, i = e.length; r < i; ++r)
                    (a = e[r]),
                        (n = o.indexOf(a)) === -1
                            ? l.push([a, 1])
                            : o.splice(n, 1);
                for (r = 0, i = o.length; r < i; ++r) l.push([o[r], -1]);
                return l;
            },
            rasterize: function (t) {
                return Math.round(t * r) / r;
            },
        };
    function i(t, e) {
        var r = e.x,
            n = e.y;
        if (r === null) return { x: 0, y: -1 };
        if (n === null) return { x: 1, y: 0 };
        var i = t.x - r,
            a = t.y - n,
            o = Math.sqrt(i * i + a * a);
        return { x: o ? i / o : 0, y: o ? a / o : -1 };
    }
    var a = 0,
        o = 1,
        l = 2,
        s = 4,
        u = 8;
    function d(t, e, r) {
        var n = a;
        return (
            t < r.left ? (n |= o) : t > r.right && (n |= l),
            e < r.top ? (n |= u) : e > r.bottom && (n |= s),
            n
        );
    }
    function f(t, e) {
        var r,
            n,
            i = e.anchor,
            a = t;
        return (
            e.clamp &&
                (a = (function (t, e) {
                    for (
                        var r,
                            n,
                            i,
                            a = t.x0,
                            f = t.y0,
                            c = t.x1,
                            h = t.y1,
                            x = d(a, f, e),
                            y = d(c, h, e);
                        x | y && !(x & y);

                    )
                        (r = x || y) & u
                            ? ((n = a + ((c - a) * (e.top - f)) / (h - f)),
                              (i = e.top))
                            : r & s
                            ? ((n = a + ((c - a) * (e.bottom - f)) / (h - f)),
                              (i = e.bottom))
                            : r & l
                            ? ((i = f + ((h - f) * (e.right - a)) / (c - a)),
                              (n = e.right))
                            : r & o &&
                              ((i = f + ((h - f) * (e.left - a)) / (c - a)),
                              (n = e.left)),
                            r === x
                                ? (x = d((a = n), (f = i), e))
                                : (y = d((c = n), (h = i), e));
                    return { x0: a, x1: c, y0: f, y1: h };
                })(a, e.area)),
            i === "start"
                ? ((r = a.x0), (n = a.y0))
                : i === "end"
                ? ((r = a.x1), (n = a.y1))
                : ((r = (a.x0 + a.x1) / 2), (n = (a.y0 + a.y1) / 2)),
            (function (t, e, r, n, i) {
                switch (i) {
                    case "center":
                        r = n = 0;
                        break;
                    case "bottom":
                        (r = 0), (n = 1);
                        break;
                    case "right":
                        (r = 1), (n = 0);
                        break;
                    case "left":
                        (r = -1), (n = 0);
                        break;
                    case "top":
                        (r = 0), (n = -1);
                        break;
                    case "start":
                        (r = -r), (n = -n);
                        break;
                    case "end":
                        break;
                    default:
                        (i *= Math.PI / 180),
                            (r = Math.cos(i)),
                            (n = Math.sin(i));
                }
                return { x: t, y: e, vx: r, vy: n };
            })(r, n, t.vx, t.vy, e.align)
        );
    }
    var c = {
            arc: function (t, e) {
                var r = (t.startAngle + t.endAngle) / 2,
                    n = Math.cos(r),
                    i = Math.sin(r),
                    a = t.innerRadius,
                    o = t.outerRadius;
                return f(
                    {
                        x0: t.x + n * a,
                        y0: t.y + i * a,
                        x1: t.x + n * o,
                        y1: t.y + i * o,
                        vx: n,
                        vy: i,
                    },
                    e
                );
            },
            point: function (t, e) {
                var r = i(t, e.origin),
                    n = r.x * t.radius,
                    a = r.y * t.radius;
                return f(
                    {
                        x0: t.x - n,
                        y0: t.y - a,
                        x1: t.x + n,
                        y1: t.y + a,
                        vx: r.x,
                        vy: r.y,
                    },
                    e
                );
            },
            rect: function (t, e) {
                var r = i(t, e.origin),
                    n = t.x,
                    a = t.y,
                    o = 0,
                    l = 0;
                return (
                    t.horizontal
                        ? ((n = Math.min(t.x, t.base)),
                          (o = Math.abs(t.base - t.x)))
                        : ((a = Math.min(t.y, t.base)),
                          (l = Math.abs(t.base - t.y))),
                    f(
                        {
                            x0: n,
                            y0: a + l,
                            x1: n + o,
                            y1: a,
                            vx: r.x,
                            vy: r.y,
                        },
                        e
                    )
                );
            },
            fallback: function (t, e) {
                var r = i(t, e.origin);
                return f(
                    { x0: t.x, y0: t.y, x1: t.x, y1: t.y, vx: r.x, vy: r.y },
                    e
                );
            },
        },
        h = t.helpers,
        x = n.rasterize;
    function y(t) {
        var e = t._model.horizontal,
            r = t._scale || (e && t._xScale) || t._yScale;
        if (!r) return null;
        if (void 0 !== r.xCenter && void 0 !== r.yCenter)
            return { x: r.xCenter, y: r.yCenter };
        var n = r.getBasePixel();
        return e ? { x: n, y: null } : { x: null, y: n };
    }
    function v(t, e, r) {
        var n = t.shadowBlur,
            i = r.stroked,
            a = x(r.x),
            o = x(r.y),
            l = x(r.w);
        i && t.strokeText(e, a, o, l),
            r.filled &&
                (n && i && (t.shadowBlur = 0),
                t.fillText(e, a, o, l),
                n && i && (t.shadowBlur = n));
    }
    var _ = function (t, e, r, n) {
        var i = this;
        (i._config = t),
            (i._index = n),
            (i._model = null),
            (i._rects = null),
            (i._ctx = e),
            (i._el = r);
    };
    h.extend(_.prototype, {
        _modelize: function (e, r, i, a) {
            var o,
                l = this._index,
                s = h.options.resolve,
                u = n.parseFont(s([i.font, {}], a, l)),
                d = s([i.color, t.defaults.global.defaultFontColor], a, l);
            return {
                align: s([i.align, "center"], a, l),
                anchor: s([i.anchor, "center"], a, l),
                area: a.chart.chartArea,
                backgroundColor: s([i.backgroundColor, null], a, l),
                borderColor: s([i.borderColor, null], a, l),
                borderRadius: s([i.borderRadius, 0], a, l),
                borderWidth: s([i.borderWidth, 0], a, l),
                clamp: s([i.clamp, !1], a, l),
                clip: s([i.clip, !1], a, l),
                color: d,
                display: e,
                font: u,
                lines: r,
                offset: s([i.offset, 0], a, l),
                opacity: s([i.opacity, 1], a, l),
                origin: y(this._el),
                padding: h.options.toPadding(s([i.padding, 0], a, l)),
                positioner:
                    ((o = this._el),
                    o instanceof t.elements.Arc
                        ? c.arc
                        : o instanceof t.elements.Point
                        ? c.point
                        : o instanceof t.elements.Rectangle
                        ? c.rect
                        : c.fallback),
                rotation: s([i.rotation, 0], a, l) * (Math.PI / 180),
                size: n.textSize(this._ctx, r, u),
                textAlign: s([i.textAlign, "start"], a, l),
                textShadowBlur: s([i.textShadowBlur, 0], a, l),
                textShadowColor: s([i.textShadowColor, d], a, l),
                textStrokeColor: s([i.textStrokeColor, d], a, l),
                textStrokeWidth: s([i.textStrokeWidth, 0], a, l),
            };
        },
        update: function (t) {
            var e,
                r,
                i,
                a = this,
                o = null,
                l = null,
                s = a._index,
                u = a._config,
                d = h.options.resolve([u.display, !0], t, s);
            d &&
                ((e = t.dataset.data[s]),
                (r = h.valueOrDefault(h.callback(u.formatter, [e, t]), e)),
                (i = h.isNullOrUndef(r) ? [] : n.toTextLines(r)).length &&
                    (l = (function (t) {
                        var e = t.borderWidth || 0,
                            r = t.padding,
                            n = t.size.height,
                            i = t.size.width,
                            a = -i / 2,
                            o = -n / 2;
                        return {
                            frame: {
                                x: a - r.left - e,
                                y: o - r.top - e,
                                w: i + r.width + 2 * e,
                                h: n + r.height + 2 * e,
                            },
                            text: { x: a, y: o, w: i, h: n },
                        };
                    })((o = a._modelize(d, i, u, t))))),
                (a._model = o),
                (a._rects = l);
        },
        geometry: function () {
            return this._rects ? this._rects.frame : {};
        },
        rotation: function () {
            return this._model ? this._model.rotation : 0;
        },
        visible: function () {
            return this._model && this._model.opacity;
        },
        model: function () {
            return this._model;
        },
        draw: function (t, e) {
            var r,
                i = t.ctx,
                a = this._model,
                o = this._rects;
            this.visible() &&
                (i.save(),
                a.clip &&
                    ((r = a.area),
                    i.beginPath(),
                    i.rect(r.left, r.top, r.right - r.left, r.bottom - r.top),
                    i.clip()),
                (i.globalAlpha = n.bound(0, a.opacity, 1)),
                i.translate(x(e.x), x(e.y)),
                i.rotate(a.rotation),
                (function (t, e, r) {
                    var n = r.backgroundColor,
                        i = r.borderColor,
                        a = r.borderWidth;
                    (n || (i && a)) &&
                        (t.beginPath(),
                        h.canvas.roundedRect(
                            t,
                            x(e.x) + a / 2,
                            x(e.y) + a / 2,
                            x(e.w) - a,
                            x(e.h) - a,
                            r.borderRadius
                        ),
                        t.closePath(),
                        n && ((t.fillStyle = n), t.fill()),
                        i &&
                            a &&
                            ((t.strokeStyle = i),
                            (t.lineWidth = a),
                            (t.lineJoin = "miter"),
                            t.stroke()));
                })(i, o.frame, a),
                (function (t, e, r, n) {
                    var i,
                        a = n.textAlign,
                        o = n.color,
                        l = Boolean(o),
                        s = n.font,
                        u = e.length,
                        d = n.textStrokeColor,
                        f = n.textStrokeWidth,
                        c = d && f;
                    if (u && (l || c))
                        for (
                            r = (function (t, e, r) {
                                var n = r.lineHeight,
                                    i = t.w,
                                    a = t.x;
                                return (
                                    e === "center"
                                        ? (a += i / 2)
                                        : (e !== "end" && e !== "right") ||
                                          (a += i),
                                    { h: n, w: i, x: a, y: t.y + n / 2 }
                                );
                            })(r, a, s),
                                t.font = s.string,
                                t.textAlign = a,
                                t.textBaseline = "middle",
                                t.shadowBlur = n.textShadowBlur,
                                t.shadowColor = n.textShadowColor,
                                l && (t.fillStyle = o),
                                c &&
                                    ((t.lineJoin = "round"),
                                    (t.lineWidth = f),
                                    (t.strokeStyle = d)),
                                i = 0,
                                u = e.length;
                            i < u;
                            ++i
                        )
                            v(t, e[i], {
                                stroked: c,
                                filled: l,
                                w: r.w,
                                x: r.x,
                                y: r.y + r.h * i,
                            });
                })(i, a.lines, o.text, a),
                i.restore());
        },
    });
    var b = t.helpers,
        p = Number.MIN_SAFE_INTEGER || -9007199254740991,
        g = Number.MAX_SAFE_INTEGER || 9007199254740991;
    function m(t, e, r) {
        var n = Math.cos(r),
            i = Math.sin(r),
            a = e.x,
            o = e.y;
        return {
            x: a + n * (t.x - a) - i * (t.y - o),
            y: o + i * (t.x - a) + n * (t.y - o),
        };
    }
    function w(t, e) {
        var r,
            n,
            i,
            a,
            o,
            l = g,
            s = p,
            u = e.origin;
        for (r = 0; r < t.length; ++r)
            (i = (n = t[r]).x - u.x),
                (a = n.y - u.y),
                (o = e.vx * i + e.vy * a),
                (l = Math.min(l, o)),
                (s = Math.max(s, o));
        return { min: l, max: s };
    }
    function k(t, e) {
        var r = e.x - t.x,
            n = e.y - t.y,
            i = Math.sqrt(r * r + n * n);
        return { vx: (e.x - t.x) / i, vy: (e.y - t.y) / i, origin: t, ln: i };
    }
    var M = function () {
        (this._rotation = 0), (this._rect = { x: 0, y: 0, w: 0, h: 0 });
    };
    function S(t, e, r) {
        var n = e.positioner(t, e),
            i = n.vx,
            a = n.vy;
        if (!i && !a) return { x: n.x, y: n.y };
        var o = r.w,
            l = r.h,
            s = e.rotation,
            u =
                Math.abs((o / 2) * Math.cos(s)) +
                Math.abs((l / 2) * Math.sin(s)),
            d =
                Math.abs((o / 2) * Math.sin(s)) +
                Math.abs((l / 2) * Math.cos(s)),
            f = 1 / Math.max(Math.abs(i), Math.abs(a));
        return (
            (u *= i * f),
            (d *= a * f),
            (u += e.offset * i),
            (d += e.offset * a),
            { x: n.x + u, y: n.y + d }
        );
    }
    b.extend(M.prototype, {
        center: function () {
            var t = this._rect;
            return { x: t.x + t.w / 2, y: t.y + t.h / 2 };
        },
        update: function (t, e, r) {
            (this._rotation = r),
                (this._rect = { x: e.x + t.x, y: e.y + t.y, w: e.w, h: e.h });
        },
        contains: function (t) {
            var e = this._rect;
            return !(
                (t = m(t, this.center(), -this._rotation)).x < e.x - 1 ||
                t.y < e.y - 1 ||
                t.x > e.x + e.w + 2 ||
                t.y > e.y + e.h + 2
            );
        },
        intersects: function (t) {
            var e,
                r,
                n,
                i = this._points(),
                a = t._points(),
                o = [k(i[0], i[1]), k(i[0], i[3])];
            for (
                this._rotation !== t._rotation &&
                    o.push(k(a[0], a[1]), k(a[0], a[3])),
                    e = 0;
                e < o.length;
                ++e
            )
                if (
                    ((r = w(i, o[e])),
                    (n = w(a, o[e])),
                    r.max < n.min || n.max < r.min)
                )
                    return !1;
            return !0;
        },
        _points: function () {
            var t = this._rect,
                e = this._rotation,
                r = this.center();
            return [
                m({ x: t.x, y: t.y }, r, e),
                m({ x: t.x + t.w, y: t.y }, r, e),
                m({ x: t.x + t.w, y: t.y + t.h }, r, e),
                m({ x: t.x, y: t.y + t.h }, r, e),
            ];
        },
    });
    var C = {
            prepare: function (t) {
                var e,
                    r,
                    n,
                    i,
                    a,
                    o = [];
                for (e = 0, n = t.length; e < n; ++e)
                    for (r = 0, i = t[e].length; r < i; ++r)
                        (a = t[e][r]),
                            o.push(a),
                            (a.$layout = {
                                _box: new M(),
                                _hidable: !1,
                                _visible: !0,
                                _set: e,
                                _idx: r,
                            });
                return (
                    o.sort(function (t, e) {
                        var r = t.$layout,
                            n = e.$layout;
                        return r._idx === n._idx
                            ? r._set - n._set
                            : n._idx - r._idx;
                    }),
                    this.update(o),
                    o
                );
            },
            update: function (t) {
                var e,
                    r,
                    n,
                    i,
                    a,
                    o = !1;
                for (e = 0, r = t.length; e < r; ++e)
                    (i = (n = t[e]).model()),
                        ((a = n.$layout)._hidable = i && i.display === "auto"),
                        (a._visible = n.visible()),
                        (o |= a._hidable);
                o &&
                    (function (t) {
                        var e, r, n, i, a, o;
                        for (e = 0, r = t.length; e < r; ++e)
                            (i = (n = t[e]).$layout)._visible &&
                                ((a = n.geometry()),
                                (o = S(n._el._model, n.model(), a)),
                                i._box.update(o, a, n.rotation()));
                        (function (t, e) {
                            var r, n, i, a;
                            for (r = t.length - 1; r >= 0; --r)
                                for (
                                    i = t[r].$layout, n = r - 1;
                                    n >= 0 && i._visible;
                                    --n
                                )
                                    (a = t[n].$layout)._visible &&
                                        i._box.intersects(a._box) &&
                                        e(i, a);
                        })(t, function (t, e) {
                            var r = t._hidable,
                                n = e._hidable;
                            (r && n) || n
                                ? (e._visible = !1)
                                : r && (t._visible = !1);
                        });
                    })(t);
            },
            lookup: function (t, e) {
                var r, n;
                for (r = t.length - 1; r >= 0; --r)
                    if ((n = t[r].$layout) && n._visible && n._box.contains(e))
                        return { dataset: n._set, label: t[r] };
                return null;
            },
            draw: function (t, e) {
                var r, n, i, a, o, l;
                for (r = 0, n = e.length; r < n; ++r)
                    (a = (i = e[r]).$layout)._visible &&
                        ((o = i.geometry()),
                        (l = S(i._el._view, i.model(), o)),
                        a._box.update(l, o, i.rotation()),
                        i.draw(t, l));
            },
        },
        z = t.helpers,
        A = {
            align: "center",
            anchor: "center",
            backgroundColor: null,
            borderColor: null,
            borderRadius: 0,
            borderWidth: 0,
            clamp: !1,
            clip: !1,
            color: void 0,
            display: !0,
            font: {
                family: void 0,
                lineHeight: 1.2,
                size: void 0,
                style: void 0,
                weight: null,
            },
            formatter: function (t) {
                if (z.isNullOrUndef(t)) return null;
                var e,
                    r,
                    n,
                    i = t;
                if (z.isObject(t))
                    if (z.isNullOrUndef(t.label))
                        if (z.isNullOrUndef(t.r))
                            for (
                                i = "", n = 0, r = (e = Object.keys(t)).length;
                                n < r;
                                ++n
                            )
                                i +=
                                    (n !== 0 ? ", " : "") +
                                    e[n] +
                                    ": " +
                                    t[e[n]];
                        else i = t.r;
                    else i = t.label;
                return String(i);
            },
            listeners: {},
            offset: 4,
            opacity: 1,
            padding: { top: 4, right: 4, bottom: 4, left: 4 },
            rotation: 0,
            textAlign: "start",
            textStrokeColor: void 0,
            textStrokeWidth: 0,
            textShadowBlur: 0,
            textShadowColor: void 0,
        },
        O = t.helpers,
        D = "$datalabels";
    function $(t, e, r) {
        var n = e && e[r.dataset];
        if (n) {
            var i = r.label,
                a = i.$context;
            !0 === O.callback(n, [a]) && ((t[D]._dirty = !0), i.update(a));
        }
    }
    function P(t, e) {
        var r,
            n,
            i = t[D],
            a = i._listeners;
        if (a.enter || a.leave) {
            if (e.type === "mousemove") n = C.lookup(i._labels, e);
            else if (e.type !== "mouseout") return;
            (r = i._hovered),
                (i._hovered = n),
                (function (t, e, r, n) {
                    var i, a;
                    (r || n) &&
                        (r
                            ? n
                                ? r.label !== n.label && (a = i = !0)
                                : (a = !0)
                            : (i = !0),
                        a && $(t, e.leave, r),
                        i && $(t, e.enter, n));
                })(t, a, r, n);
        }
    }
    t.defaults.global.plugins.datalabels = A;
    var N = {
        id: "datalabels",
        beforeInit: function (t) {
            t[D] = { _actives: [] };
        },
        beforeUpdate: function (t) {
            var e = t[D];
            (e._listened = !1),
                (e._listeners = {}),
                (e._datasets = []),
                (e._labels = []);
        },
        afterDatasetUpdate: function (t, e, r) {
            var n,
                i,
                a,
                o = e.index,
                l = t[D],
                s = (l._datasets[o] = []),
                u = t.isDatasetVisible(o),
                d = t.data.datasets[o],
                f = (function (t, e) {
                    var r = t.datalabels;
                    return !1 === r
                        ? null
                        : (!0 === r && (r = {}), O.merge({}, [e, r]));
                })(d, r),
                c = e.meta.data || [],
                h = c.length,
                x = t.ctx;
            for (x.save(), n = 0; n < h; ++n)
                (i = c[n]),
                    u && i && !i.hidden && !i._model.skip
                        ? (s.push((a = new _(f, x, i, n))),
                          a.update(
                              (a.$context = {
                                  active: !1,
                                  chart: t,
                                  dataIndex: n,
                                  dataset: d,
                                  datasetIndex: o,
                              })
                          ))
                        : (a = null),
                    (i[D] = a);
            x.restore(),
                O.merge(l._listeners, f.listeners || {}, {
                    merger: function (t, r, n) {
                        (r[t] = r[t] || {}),
                            (r[t][e.index] = n[t]),
                            (l._listened = !0);
                    },
                });
        },
        afterUpdate: function (t, e) {
            t[D]._labels = C.prepare(t[D]._datasets, e);
        },
        afterDatasetsDraw: function (t) {
            C.draw(t, t[D]._labels);
        },
        beforeEvent: function (t, e) {
            if (t[D]._listened)
                switch (e.type) {
                    case "mousemove":
                    case "mouseout":
                        P(t, e);
                        break;
                    case "click":
                        !(function (t, e) {
                            var r = t[D],
                                n = r._listeners.click,
                                i = n && C.lookup(r._labels, e);
                            i && $(t, n, i);
                        })(t, e);
                }
        },
        afterEvent: function (e) {
            var r,
                i,
                a,
                o,
                l = e[D],
                s = l._actives,
                u = (l._actives = e.lastActive || []),
                d = n.arrayDiff(s, u);
            for (r = 0, i = d.length; r < i; ++r)
                (a = d[r])[1] &&
                    (o = a[0][D]) &&
                    ((o.$context.active = a[1] === 1), o.update(o.$context));
            (l._dirty || d.length) &&
                (C.update(l._labels),
                (function (e) {
                    if (!e.animating) {
                        for (
                            var r = t.animationService.animations,
                                n = 0,
                                i = r.length;
                            n < i;
                            ++n
                        )
                            if (r[n].chart === e) return;
                        e.render({ duration: 1, lazy: !0 });
                    }
                })(e)),
                delete l._dirty;
        },
    };
    return t.plugins.register(N), N;
});
