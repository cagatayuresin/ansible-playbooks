(function () {
  var path = window.location.pathname || "/";
  var inTr = path.indexOf("/tr/") !== -1 || /\/tr\/?$/.test(path);

  function hrefIsTr(href) {
    if (!href) return false;
    return href.indexOf("/tr/") !== -1 || /\/tr\/?$/.test(href);
  }

  document.querySelectorAll("nav .nav-list-link").forEach(function (link) {
    var li = link.closest(".nav-list-item");
    if (!li) return;
    var isTrLink = hrefIsTr(link.getAttribute("href"));
    if (inTr ? !isTrLink : isTrLink) {
      li.style.display = "none";
    }
  });

  function withTr(pathname) {
    var parts = pathname.split("/").filter(Boolean);
    if (parts[0] === "ansible-playbooks") {
      if (parts[1] !== "tr") parts.splice(1, 0, "tr");
    } else if (parts[0] !== "tr") {
      parts.unshift("tr");
    }
    return "/" + parts.join("/") + "/";
  }

  function withoutTr(pathname) {
    var parts = pathname.split("/").filter(Boolean);
    var idx = parts.indexOf("tr");
    if (idx !== -1) parts.splice(idx, 1);
    return parts.length ? "/" + parts.join("/") + "/" : "/";
  }

  var en = document.getElementById("lang-switch-en");
  var tr = document.getElementById("lang-switch-tr");
  if (en) {
    en.href = withoutTr(path);
    if (!inTr) en.setAttribute("aria-current", "page");
  }
  if (tr) {
    tr.href = withTr(path);
    if (inTr) tr.setAttribute("aria-current", "page");
  }
})();
