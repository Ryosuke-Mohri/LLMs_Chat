(function() {
    var doc = window.parent.document;
    // Strategy 1: Escape key
    doc.dispatchEvent(new KeyboardEvent('keydown', {
        key: 'Escape', code: 'Escape', keyCode: 27, which: 27, bubbles: true
    }));
    // Strategy 2: Body click (closes popover by clicking outside)
    doc.body.click();
})();
