<!--
PayLES readme

to run:
navigate to: \Documents\Github\Payles
run: python -m app.main

todo:
add in rows from paydf_template
create levdf (leave calculator)
instructions page and overlay on example les
update pay active and drill pay in config
add more resources
add drill pay
account for specific pays
update readme
refactor javascript
check what all is saved if in combat zone (are state taxes paid?)
total tsp deduction per year and contribution limits, max tsp percentage
add modals
joint spouse with two LES's
recommendations tab (like if not adding to tsp, put in money)
rework drag and drop functionality


possible:
create unit tests


end of project:
minify style.css and script.js when pushed into a production environment
normalize css: https://necolas.github.io/normalize.css/
use python cProfile or line_profiler to find bottlenecks
check mobile use
instructions for self-host



3. Security Headers

HTTP headers that instruct browsers to enforce security policies.
Common headers for Flask apps:
Content-Security-Policy: restricts sources for scripts, styles, etc.
X-Frame-Options: prevents clickjacking by disallowing your site in iframes.
X-Content-Type-Options: nosniff: prevents MIME type sniffing.
Strict-Transport-Security: enforces HTTPS.
You can set these headers in Flask using an after_request handler.
Why it matters:
Helps prevent XSS, clickjacking, and other browser-based attacks.





function attachTspBaseListeners() {
    document.querySelectorAll('input[data-header="Trad TSP Base Rate"], input[data-header="Roth TSP Base Rate"]').forEach(function(input) {
        input.removeEventListener('input', updateTspInputs); // Prevent duplicate listeners
        input.removeEventListener('change', updateTspInputs);
        input.addEventListener('input', updateTspInputs);
        input.addEventListener('change', updateTspInputs);
    });
}




// =========================
// TSP dynamic enable/disable
// =========================
function showTspNotification(message) {
    let notif = document.getElementById('tsp-notification');
    if (!notif) {
        notif = document.createElement('div');
        notif.id = 'tsp-notification';
        notif.style.position = 'fixed';
        notif.style.top = '20px';
        notif.style.left = '50%';
        notif.style.transform = 'translateX(-50%)';
        notif.style.background = '#ffcccc';
        notif.style.color = '#900';
        notif.style.padding = '10px 20px';
        notif.style.borderRadius = '5px';
        notif.style.zIndex = '1000';
        notif.style.fontWeight = 'bold';
        document.body.appendChild(notif);
    }
    notif.textContent = message;
    notif.style.display = 'block';
    setTimeout(() => { notif.style.display = 'none'; }, 4000);
}

function updateTspInputs() {
    const tradBaseInput = document.querySelector('input[data-header="Trad TSP Base Rate"]');
    const rothBaseInput = document.querySelector('input[data-header="Roth TSP Base Rate"]');
    const tradBaseValue = tradBaseInput ? parseInt(tradBaseInput.value || tradBaseInput.placeholder || "0", 10) : 0;
    const rothBaseValue = rothBaseInput ? parseInt(rothBaseInput.value || rothBaseInput.placeholder || "0", 10) : 0;

    let invalidSpecialty = false;

    document.querySelectorAll('.tsp-rate-input').forEach(function(input) {
        const header = input.getAttribute('data-header');
        const type = input.getAttribute('data-tsp-type');
        if (header === "Trad TSP Base Rate" || header === "Roth TSP Base Rate") {
            input.disabled = false;
            return;
        }
        if (type === "trad" && tradBaseValue < 1) {
            input.disabled = true;
            if (parseInt(input.value || "0", 10) > 0) invalidSpecialty = true;
            input.value = "";
        } else if (type === "roth" && rothBaseValue < 1) {
            input.disabled = true;
            if (parseInt(input.value || "0", 10) > 0) invalidSpecialty = true;
            input.value = "";
        } else {
            input.disabled = false;
        }
    });

    // Gray out update buttons if invalid
    const buttonIds = [
        'update-les-button',
        'add-entitlement-button',
        'add-deduction-button',
        'export-button'
    ];
    buttonIds.forEach(function(id) {
        const btn = document.getElementById(id);
        if (btn) {
            btn.disabled = invalidSpecialty || editingIndex !== null;
        }
    });

    // Show notification if invalid
    if (invalidSpecialty) {
        showTspNotification("TSP Specialty/Incentive/Bonus Rates cannot be used unless Base Rate is greater than 0.");
    }
}

-->
