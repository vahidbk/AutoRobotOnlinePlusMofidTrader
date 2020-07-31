// ==UserScript==
// @name         AutoClick Mobile MofidTrader
// @namespace    http://VB.net/
// @version      0.1
// @description  autoClick
// @author       me
// @match        *mobile.emofid.com/stock-details/*
// @grant        none
// ==/UserScript==

(function() {
    setInterval(function(){

        var btn = document.querySelector("[type='submit']");
        var autoClickbtn = document.querySelector("[id='NewRobotButton']");
        if (btn && !autoClickbtn)
        {
            var element = document.createElement("input");
            element.setAttribute("type", "button");
            element.setAttribute("value", "AutoClick300ms=Disable");
            element.setAttribute("name", "RobotButton");
            element.setAttribute("id", "NewRobotButton");
            element.setAttribute("onclick", 'document.querySelector("[id=\'NewRobotButton\']").value = (document.querySelector("[id=\'NewRobotButton\']").value=="AutoClick300ms=Disable" ? "AutoClick300ms=Enable" : "AutoClick300ms=Disable");');
            btn.parentNode.appendChild(element);
            autoClickbtn = element;
        }

        if (btn)
            if (autoClickbtn.value=="AutoClick300ms=Enable")
            {
                btn.click();
                console.log('clicked');
            }
    },300);
})();