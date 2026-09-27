(function () {
  function setCursor(gd, cursor) {
    gd.querySelectorAll(".nsewdrag").forEach(function (el) {
      el.style.cursor = cursor;
    });
  }

  function attach(gd) {
    if (!gd || gd.__candidatosPointer) return;
    if (typeof gd.on !== "function") return;
    gd.__candidatosPointer = true;
    gd.on("plotly_hover", function (e) {
      if (e && e.points && e.points.length) setCursor(gd, "pointer");
    });
    gd.on("plotly_unhover", function () {
      setCursor(gd, "");
    });
    gd.on("plotly_click", function () {
      setCursor(gd, "");
    });
  }

  function scan() {
    document.querySelectorAll(".js-plotly-plot").forEach(attach);
  }

  function boot() {
    scan();
    new MutationObserver(scan).observe(document.body, {
      childList: true,
      subtree: true,
      attributes: true,
      attributeFilter: ["class"],
    });
    var tentativas = 0;
    var timer = setInterval(function () {
      scan();
      if (++tentativas > 20) clearInterval(timer);
    }, 500);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", boot);
  } else {
    boot();
  }
})();
