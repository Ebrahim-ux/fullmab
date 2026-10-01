(() => {
  const expressionInput = document.getElementById("expression");
  const errorEl = document.getElementById("error");
  const historyEl = document.getElementById("history");
  const memoryIndicator = document.getElementById("memory-indicator");
  const pad = document.querySelector(".pad");

  let memory = 0;
  let memoryActive = false;
  const history = [];

  function setError(message) {
    errorEl.textContent = message || "";
  }

  function insertAtCursor(text) {
    const start = expressionInput.selectionStart ?? expressionInput.value.length;
    const end = expressionInput.selectionEnd ?? expressionInput.value.length;
    const value = expressionInput.value;
    expressionInput.value = value.slice(0, start) + text + value.slice(end);
    const cursor = start + text.length;
    expressionInput.setSelectionRange(cursor, cursor);
    expressionInput.focus();
  }

  function backspace() {
    const start = expressionInput.selectionStart ?? expressionInput.value.length;
    const end = expressionInput.selectionEnd ?? expressionInput.value.length;
    const value = expressionInput.value;

    if (start !== end) {
      expressionInput.value = value.slice(0, start) + value.slice(end);
      expressionInput.setSelectionRange(start, start);
    } else if (start > 0) {
      expressionInput.value = value.slice(0, start - 1) + value.slice(start);
      expressionInput.setSelectionRange(start - 1, start - 1);
    }
    expressionInput.focus();
  }

  function clearAll() {
    expressionInput.value = "";
    setError("");
    expressionInput.focus();
  }

  function renderHistory() {
    historyEl.innerHTML = "";
    for (const entry of history) {
      const item = document.createElement("div");
      item.className = "history-item";

      const exprSpan = document.createElement("span");
      exprSpan.textContent = entry.expression;
      const resultSpan = document.createElement("span");
      resultSpan.textContent = `= ${entry.result}`;
      item.append(exprSpan, resultSpan);

      item.addEventListener("click", () => {
        expressionInput.value = String(entry.result);
        expressionInput.focus();
      });
      historyEl.appendChild(item);
    }
  }

  function updateMemoryIndicator() {
    memoryIndicator.classList.toggle("active", memoryActive);
    memoryIndicator.textContent = memoryActive ? "M" : "";
  }

  // The UI shows "^" for exponentiation since it's the familiar calculator
  // symbol; the backend evaluator expects Python's "**".
  function toServerExpression(raw) {
    return raw.replace(/\^/g, "**");
  }

  async function evaluateExpression() {
    const raw = expressionInput.value.trim();
    if (!raw) {
      return;
    }

    try {
      const response = await fetch("/api/calculate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ expression: toServerExpression(raw) }),
      });
      const data = await response.json();

      if (!response.ok) {
        setError(data.error || "Invalid expression");
        return;
      }

      setError("");
      history.push({ expression: raw, result: data.result });
      if (history.length > 20) {
        history.shift();
      }
      renderHistory();
      expressionInput.value = String(data.result);
      expressionInput.setSelectionRange(
        expressionInput.value.length,
        expressionInput.value.length,
      );
    } catch (err) {
      setError("Network error - could not reach the calculator service");
    }
  }

  function currentDisplayNumber() {
    const value = Number.parseFloat(expressionInput.value);
    return Number.isFinite(value) ? value : 0;
  }

  const actions = {
    clear: clearAll,
    backspace,
    equals: evaluateExpression,
    "memory-clear": () => {
      memory = 0;
      memoryActive = false;
      updateMemoryIndicator();
    },
    "memory-recall": () => {
      insertAtCursor(String(memory));
    },
    "memory-add": () => {
      memory += currentDisplayNumber();
      memoryActive = true;
      updateMemoryIndicator();
    },
    "memory-subtract": () => {
      memory -= currentDisplayNumber();
      memoryActive = true;
      updateMemoryIndicator();
    },
  };

  pad.addEventListener("click", (event) => {
    const button = event.target.closest("button");
    if (!button) return;

    const insert = button.dataset.insert;
    const action = button.dataset.action;

    if (insert !== undefined) {
      insertAtCursor(insert);
      return;
    }
    if (action && actions[action]) {
      actions[action]();
    }
  });

  expressionInput.addEventListener("keydown", (event) => {
    if (event.key === "Enter") {
      event.preventDefault();
      evaluateExpression();
    } else if (event.key === "Escape") {
      clearAll();
    }
  });

  updateMemoryIndicator();
})();
