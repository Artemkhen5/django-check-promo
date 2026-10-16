(() => {
    const form = document.querySelector(".receipt-entry-form");

    if (!form) {
        return;
    }

    const submitButton = form.querySelector('button[type="submit"]');
    const formErrors = form.querySelector("[data-form-errors]");
    const feedback = form.querySelector("[data-form-feedback]");
    const fields = ["fn", "fd", "fp", "purchase_date", "purchase_time", "amount"];

    const getInput = (name) => form.elements.namedItem(name);

    const clearFieldError = (name) => {
        const input = getInput(name);
        const errorContainer = form.querySelector(`[data-field-error="${name}"]`);

        if (errorContainer) {
            errorContainer.replaceChildren();
            errorContainer.hidden = true;
        }

        if (input) {
            input.removeAttribute("aria-invalid");
            input.removeAttribute("aria-describedby");
        }
    };

    const showFieldError = (name, message) => {
        const input = getInput(name);
        const errorContainer = form.querySelector(`[data-field-error="${name}"]`);

        if (!input || !errorContainer || !message) {
            return;
        }

        const errorId = `${input.id}-error`;
        errorContainer.id = errorId;
        errorContainer.textContent = message;
        errorContainer.hidden = false;
        input.setAttribute("aria-invalid", "true");
        input.setAttribute("aria-describedby", errorId);
    };

    const clearFormErrors = () => {
        if (formErrors) {
            formErrors.replaceChildren();
            formErrors.hidden = true;
        }

        feedback.replaceChildren();
        feedback.hidden = true;
        feedback.classList.remove("receipt-entry-form__feedback--success", "receipt-entry-form__feedback--error");
    };

    const showFormErrors = (messages) => {
        formErrors.replaceChildren();
        const list = document.createElement("ul");
        list.className = "errorlist nonfield";

        messages.forEach((message) => {
            const item = document.createElement("li");
            item.textContent = message;
            list.append(item);
        });

        formErrors.append(list);
        formErrors.hidden = false;
    };

    const validate = () => {
        const errors = {};
        const addRequiredError = (name, label) => {
            if (!getInput(name).value.trim()) {
                errors[name] = `${label}: заполните это поле.`;
            }
        };

        addRequiredError("fn", "ФН");
        addRequiredError("fd", "Номер чека");
        addRequiredError("fp", "ФП");
        addRequiredError("purchase_date", "Дата покупки");
        addRequiredError("purchase_time", "Время покупки");
        addRequiredError("amount", "Сумма");

        ["fn", "fd", "fp"].forEach((name) => {
            const value = getInput(name).value.trim();
            if (value && !/^\d+$/.test(value)) {
                errors[name] = "Укажите только цифры.";
            }
        });

        const purchaseDate = getInput("purchase_date").value;
        if (purchaseDate && (purchaseDate < form.dataset.promoStart || purchaseDate > form.dataset.promoEnd)) {
            errors.purchase_date = `Дата должна входить в период акции: ${form.dataset.promoStart.split("-").reverse().join(".")} — ${form.dataset.promoEnd.split("-").reverse().join(".")}.`;
        }

        const amountValue = getInput("amount").value;
        if (amountValue) {
            const amount = Number(amountValue);
            if (!Number.isFinite(amount)) {
                errors.amount = "Введите корректную сумму.";
            } else if (amount < 1000) {
                errors.amount = "Сумма покупки должна быть не меньше 1 000 ₽.";
            }
        }

        return errors;
    };

    fields.forEach((name) => {
        const input = getInput(name);
        const errorContainer = form.querySelector(`[data-field-error="${name}"]`);

        if (errorContainer && !errorContainer.textContent.trim()) {
            errorContainer.hidden = true;
        }

        input.addEventListener("input", () => clearFieldError(name));
        input.addEventListener("change", () => clearFieldError(name));
    });

    form.addEventListener("submit", async (event) => {
        event.preventDefault();
        clearFormErrors();
        fields.forEach(clearFieldError);

        const errors = validate();
        const invalidNames = Object.keys(errors);

        if (invalidNames.length) {
            invalidNames.forEach((name) => showFieldError(name, errors[name]));
            getInput(invalidNames[0]).focus();
            return;
        }

        submitButton.disabled = true;
        submitButton.dataset.originalText = submitButton.textContent;
        submitButton.textContent = "Отправляем…";

        try {
            const response = await fetch(form.action || window.location.href, {
                method: "POST",
                body: new FormData(form),
                credentials: "same-origin",
                headers: { Accept: "application/json" },
            });
            const result = await response.json();

            if (response.ok) {
                feedback.classList.add("receipt-entry-form__feedback--success");
                feedback.textContent = result.message || "Чек отправлен на проверку.";
                feedback.hidden = false;
                form.reset();

                if (result.redirect_url) {
                    const link = document.createElement("a");
                    link.href = result.redirect_url;
                    link.textContent = "Перейти к моим чекам";
                    feedback.append(" ", link);
                }
            } else if (result.errors) {
                const nonFieldErrors = result.errors.__all__ || [];

                Object.entries(result.errors).forEach(([name, messages]) => {
                    if (name !== "__all__" && fields.includes(name) && messages.length) {
                        showFieldError(name, messages[0]);
                    }
                });

                if (nonFieldErrors.length) {
                    showFormErrors(nonFieldErrors);
                }
            } else {
                throw new Error("Unexpected server response");
            }
        } catch (error) {
            feedback.classList.add("receipt-entry-form__feedback--error");
            feedback.textContent = "Не удалось отправить чек. Проверьте подключение и попробуйте ещё раз.";
            feedback.hidden = false;
        } finally {
            submitButton.disabled = false;
            submitButton.textContent = submitButton.dataset.originalText;
        }
    });
})();
