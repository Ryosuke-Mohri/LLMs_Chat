(function() {
    var doc = window.parent.document;
    function markDangerButtons() {
        doc.querySelectorAll('.danger-btn-marker').forEach(function(marker) {
            var container = marker.closest('[data-testid="stElementContainer"]') ||
                            marker.closest('[data-testid="element-container"]') ||
                            marker.parentElement && marker.parentElement.parentElement;
            if (!container) return;
            var next = container.nextElementSibling;
            if (!next) return;
            var btn = next.querySelector('button');
            if (btn && !btn.hasAttribute('data-danger')) {
                btn.setAttribute('data-danger', 'true');
            }
        });
    }
    // 初回実行 + MutationObserver で動的変更に対応
    setTimeout(markDangerButtons, 300);
    setTimeout(markDangerButtons, 1000);
    var obs = new MutationObserver(function() { setTimeout(markDangerButtons, 50); });
    obs.observe(doc.body, { childList: true, subtree: true });
})();
