/**
 * main.js — Dashboard interactivity
 */
document.addEventListener("DOMContentLoaded", () => {

    /* ----- Plate search filter ----- */
    const searchInput = document.getElementById("search-plate");
    const statusFilter = document.getElementById("status-filter");
    const tbody = document.getElementById("inspection-tbody");

    function filterTable() {
        if (!tbody) return;
        const query = (searchInput?.value || "").toLowerCase();
        const status = statusFilter?.value || "all";

        tbody.querySelectorAll("tr").forEach(row => {
            const plate = (row.querySelector(".cell-plate")?.textContent || "").toLowerCase();
            const badge = row.querySelector(".badge");
            const rowStatus = badge?.classList.contains("badge-safe") ? "safe" :
                badge?.classList.contains("badge-unsafe") ? "unsafe" : "";

            const matchPlate = !query || plate.includes(query);
            const matchStatus = status === "all" || rowStatus === status;

            row.style.display = (matchPlate && matchStatus) ? "" : "none";
        });
    }

    if (searchInput) searchInput.addEventListener("input", filterTable);
    if (statusFilter) statusFilter.addEventListener("change", filterTable);

    /* ----- Refresh button ----- */
    const refreshBtn = document.getElementById("refresh-btn");
    if (refreshBtn) {
        refreshBtn.addEventListener("click", () => {
            refreshBtn.disabled = true;
            refreshBtn.textContent = "Refreshing…";
            setTimeout(() => {
                location.reload();
            }, 600);
        });
    }

    /* ----- Notification dropdown ----- */
    const notifToggle = document.getElementById("notification-toggle");
    const notifDropdown = document.getElementById("notification-dropdown");
    if (notifToggle && notifDropdown) {
        notifToggle.addEventListener("click", (e) => {
            e.stopPropagation();
            notifDropdown.classList.toggle("open");
        });

        document.addEventListener("click", (e) => {
            if (!notifDropdown.contains(e.target)) {
                notifDropdown.classList.remove("open");
            }
        });
    }
});
