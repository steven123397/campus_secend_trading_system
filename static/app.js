document.addEventListener("DOMContentLoaded", () => {
    const authRoot = document.querySelector("[data-auth-root]");

    if (authRoot) {
        const switches = authRoot.querySelectorAll("[data-auth-switch]");
        const panels = authRoot.querySelectorAll("[data-auth-panel]");

        switches.forEach((button) => {
            button.addEventListener("click", () => {
                const target = button.dataset.authSwitch;

                switches.forEach((item) => {
                    item.classList.toggle("is-active", item === button);
                });

                panels.forEach((panel) => {
                    panel.classList.toggle("is-active", panel.dataset.authPanel === target);
                });

                authRoot.dataset.mode = target;
            });
        });
    }

    document.querySelectorAll("[data-password-meter]").forEach((input) => {
        input.addEventListener("input", () => {
            const strength = Math.min(input.value.length / 12, 1);
            const meter = input.closest("form")?.querySelector(".strength-meter span");

            input.style.setProperty("--password-strength", strength.toString());

            if (meter) {
                meter.style.transform = `scaleX(${Math.max(strength, 0.08)})`;
            }
        });
    });

    document.querySelectorAll("[data-tilt-card]").forEach((card) => {
        card.addEventListener("pointermove", (event) => {
            const rect = card.getBoundingClientRect();
            const x = (event.clientX - rect.left) / rect.width - 0.5;
            const y = (event.clientY - rect.top) / rect.height - 0.5;

            card.style.setProperty("--tilt-x", `${(-y * 6).toFixed(2)}deg`);
            card.style.setProperty("--tilt-y", `${(x * 6).toFixed(2)}deg`);
        });

        card.addEventListener("pointerleave", () => {
            card.style.setProperty("--tilt-x", "0deg");
            card.style.setProperty("--tilt-y", "0deg");
        });
    });
});
