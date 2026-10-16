(() => {
    const table = document.querySelector(".receipts-table[data-api-url]");

    if (!table) {
        return;
    }

    const rows = new Map(
        Array.from(table.querySelectorAll("tr[data-receipt-id]"), (row) => [row.dataset.receiptId, row]),
    );
    const statusLabels = {
        pending: "Чек на проверке",
        approved: "Чек принят",
        rejected: "",
        won: "Поздравляем с выигрышем!",
    };
    let requestInProgress = false;

    const createGiftIcon = () => {
        const namespace = "http://www.w3.org/2000/svg";
        const icon = document.createElementNS(namespace, "svg");
        const path = document.createElementNS(namespace, "path");

        icon.setAttribute("class", "receipt-status__gift");
        icon.setAttribute("viewBox", "0 0 20 20");
        icon.setAttribute("aria-hidden", "true");
        icon.setAttribute("focusable", "false");
        path.setAttribute(
            "d",
            "M3 8h14v9H3zM2 5.5h16V8H2zM10 5.5V17M10 5.5H6.6c-2.6 0-2.5-3 0-3C8.5 2.5 10 5.5 10 5.5Zm0 0h3.4c2.6 0 2.5-3 0-3C11.5 2.5 10 5.5 10 5.5Z",
        );
        path.setAttribute("fill", "none");
        path.setAttribute("stroke", "currentColor");
        path.setAttribute("stroke-width", "1.5");
        path.setAttribute("stroke-linecap", "round");
        path.setAttribute("stroke-linejoin", "round");
        icon.append(path);

        return icon;
    };

    const createStatusBadge = (receipt) => {
        const badge = document.createElement("span");
        badge.className = `receipt-status receipt-status--${receipt.status}`;

        if (receipt.status === "won") {
            badge.append(createGiftIcon());
        } else if (["pending", "approved", "rejected"].includes(receipt.status)) {
            const icon = document.createElement("img");
            icon.src = table.dataset[`icon${receipt.status[0].toUpperCase()}${receipt.status.slice(1)}`];
            icon.alt = "";
            badge.append(icon);
        } else {
            return null;
        }

        badge.append(document.createTextNode(receipt.status_display));
        return badge;
    };

    const updateReceipt = (receipt) => {
        const row = rows.get(String(receipt.id));

        if (!row || !Object.hasOwn(statusLabels, receipt.status)) {
            return;
        }

        const rejectionReason = receipt.rejection_reason || "";
        if (row.dataset.receiptStatus === receipt.status && row.dataset.rejectionReason === rejectionReason) {
            return;
        }

        const badge = createStatusBadge(receipt);
        const statusCell = row.querySelector("[data-receipt-status-cell]");
        const information = row.querySelector("[data-receipt-info]");

        if (badge && statusCell) {
            const currentBadge = statusCell.querySelector(".receipt-status");
            if (currentBadge) {
                currentBadge.replaceWith(badge);
            }
        }

        if (information) {
            information.textContent = receipt.status === "rejected"
                ? rejectionReason
                : statusLabels[receipt.status];
        }

        row.dataset.receiptStatus = receipt.status;
        row.dataset.rejectionReason = rejectionReason;
    };

    const refreshStatuses = async () => {
        if (requestInProgress || document.visibilityState === "hidden") {
            return;
        }

        requestInProgress = true;

        try {
            const response = await fetch(table.dataset.apiUrl, {
                method: "GET",
                credentials: "same-origin",
                cache: "no-store",
                headers: { Accept: "application/json" },
            });

            if (!response.ok) {
                return;
            }

            const payload = await response.json();
            const receipts = Array.isArray(payload) ? payload : payload.results;

            if (Array.isArray(receipts)) {
                receipts.forEach(updateReceipt);
            }
        } catch (error) {
            // Keep the page usable if the status check temporarily fails.
        } finally {
            requestInProgress = false;
        }
    };

    window.setInterval(refreshStatuses, 15000);
    document.addEventListener("visibilitychange", () => {
        if (document.visibilityState === "visible") {
            refreshStatuses();
        }
    });
})();
