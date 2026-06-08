function parseNumber(value) {
    const number = Number(String(value || "").replace(",", ".").replace(/[^\d.-]/g, ""));
    return Number.isFinite(number) ? number : 0;
}

function formatNumber(value, maximumFractionDigits = 2) {
    return new Intl.NumberFormat("ru-RU", {
        maximumFractionDigits,
    }).format(Number(value));
}

function formatPrice(price) {
    return `${formatNumber(price)} ₸`;
}

function formatInputNumber(value) {
    return Number(value.toFixed(2)).toString();
}

function getExactLength(value) {
    const match = String(value || "").trim().match(/^(\d+(?:[.,]\d+)?)\s*м$/i);
    return match ? match[1].replace(",", ".") : "";
}

function getProductElements() {
    return {
        variantControl: document.getElementById("productVariant"),
        quantityInput: document.getElementById("productQuantity"),
        priceElement: document.getElementById("productPrice"),
        totalElement: document.getElementById("productTotal"),
        totalFormula: document.getElementById("productTotalFormula"),
        whatsappButton: document.getElementById("whatsappProductButton"),
        materialCalculator: document.getElementById("productMaterialCalculator"),
        boardCountInput: document.getElementById("productBoardCount"),
        boardLengthInput: document.getElementById("productBoardLength"),
        materialResult: document.getElementById("materialCalculationResult"),
        linearMetersElement: document.getElementById("materialLinearMeters"),
        squareMetersElement: document.getElementById("materialSquareMeters"),
    };
}

function getVariantState(variantControl) {
    let name = variantControl.dataset.defaultVariant || "Стандарт";
    let price = parseNumber(variantControl.dataset.defaultPrice);

    if (variantControl.tagName === "SELECT") {
        const selectedOption = variantControl.options[variantControl.selectedIndex];
        name = selectedOption.value;
        price = parseNumber(selectedOption.dataset.price);
    }

    return { name, price };
}

function updateMaterialCalculation(elements, syncQuantity = false) {
    const {
        variantControl,
        quantityInput,
        materialCalculator,
        boardCountInput,
        boardLengthInput,
        materialResult,
        linearMetersElement,
        squareMetersElement,
    } = elements;

    if (!materialCalculator || !boardCountInput || !boardLengthInput || !materialResult) {
        return null;
    }

    const boardCount = parseNumber(boardCountInput.value);
    const boardLength = parseNumber(boardLengthInput.value);
    const widthMillimeters = parseNumber(variantControl.dataset.productWidth);

    if (boardCount <= 0 || boardLength <= 0 || widthMillimeters <= 0) {
        materialResult.hidden = true;
        return null;
    }

    const linearMeters = boardCount * boardLength;
    const squareMeters = linearMeters * (widthMillimeters / 1000);
    const productUnit = variantControl.dataset.productUnit || "";

    linearMetersElement.textContent = `${formatNumber(linearMeters)} п/м`;
    squareMetersElement.textContent = `${formatNumber(squareMeters)} м²`;
    materialResult.hidden = false;

    if (syncQuantity && quantityInput) {
        let calculatedQuantity = boardCount;

        if (productUnit === "м²") {
            calculatedQuantity = squareMeters;
        } else if (productUnit === "п/м") {
            calculatedQuantity = linearMeters;
        }

        quantityInput.value = formatInputNumber(calculatedQuantity);
    }

    return { boardCount, boardLength, linearMeters, squareMeters };
}

function updateProductState(syncQuantity = false) {
    const elements = getProductElements();
    const {
        variantControl,
        quantityInput,
        priceElement,
        totalElement,
        totalFormula,
        whatsappButton,
    } = elements;

    if (!variantControl || !priceElement || !totalElement || !whatsappButton) {
        return;
    }

    const productName = variantControl.dataset.productName || "";
    const productUnit = variantControl.dataset.productUnit || "";
    const variant = getVariantState(variantControl);
    const materialCalculation = updateMaterialCalculation(elements, syncQuantity);
    const quantity = quantityInput ? parseNumber(quantityInput.value) : 0;
    const quantityText = quantity > 0 ? `${formatNumber(quantity)} ${productUnit}` : "не указано";

    priceElement.textContent = formatPrice(variant.price);

    if (quantity > 0) {
        totalElement.textContent = formatPrice(quantity * variant.price);
        totalFormula.textContent = `${formatNumber(quantity)} ${productUnit} × ${formatPrice(variant.price)} / ${productUnit}`;
    } else {
        totalElement.textContent = "Укажите количество";
        totalFormula.textContent = `Количество × цена за ${productUnit}`;
    }

    const message = [
        "Здравствуйте! Хочу узнать наличие и цену:",
        productName,
        `Вариант: ${variant.name}`,
        `Количество: ${quantityText}`,
        `Цена на сайте: ${formatPrice(variant.price)} / ${productUnit}`,
    ];

    if (quantity > 0) {
        message.push(`Предварительная сумма: ${formatPrice(quantity * variant.price)}`);
    }

    if (materialCalculation) {
        message.push(
            `Расчёт материала: ${formatNumber(materialCalculation.boardCount)} шт × ${formatNumber(materialCalculation.boardLength)} м = ${formatNumber(materialCalculation.linearMeters)} п/м = ${formatNumber(materialCalculation.squareMeters)} м²`,
        );
    }

    const whatsappNumber = whatsappButton.dataset.whatsappNumber || "77772002742";
    whatsappButton.href = `https://wa.me/${whatsappNumber}?text=${encodeURIComponent(message.join("\n"))}`;
}

document.addEventListener("DOMContentLoaded", () => {
    const elements = getProductElements();
    const {
        variantControl,
        quantityInput,
        boardCountInput,
        boardLengthInput,
    } = elements;

    if (!variantControl) {
        return;
    }

    if (variantControl.tagName === "SELECT") {
        variantControl.addEventListener("change", () => updateProductState());
    }

    if (quantityInput) {
        quantityInput.addEventListener("input", () => updateProductState());
    }

    if (boardLengthInput) {
        boardLengthInput.value = getExactLength(variantControl.dataset.productLength);
    }

    [boardCountInput, boardLengthInput].forEach((input) => {
        if (input) {
            input.addEventListener("input", () => updateProductState(true));
        }
    });

    updateProductState();
});
