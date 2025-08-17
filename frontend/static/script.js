// State management
let selectedCalculation = "CDB/RDB"

const marketIndicators = {
  cdi: {
    rate: "12,5%",
    lastUpdate: "15/08/2025",
  },
  selic: {
    rate: "12,25%",
    lastUpdate: "15/08/2025",
  },
}

// DOM elements
const optionButtons = document.querySelectorAll(".option-button")
const calculateButton = document.getElementById("calculate-btn")

// Initialize the application
function init() {
  // Set up option button event listeners
  optionButtons.forEach((button) => {
    button.addEventListener("click", function () {
      // Remove selected class from all buttons
      optionButtons.forEach((btn) => btn.classList.remove("selected"))

      // Add selected class to clicked button
      this.classList.add("selected")

      // Update selected calculation
      selectedCalculation = this.getAttribute("data-option")

      console.log(`Selected calculation: ${selectedCalculation}`)
    })
  })

  // Set up calculate button event listener
  calculateButton.addEventListener("click", () => {
    const investmentValue = document.getElementById("investment-value").value
    const timePeriod = document.getElementById("time-period").value
    const cdiPercentage = document.getElementById("cdi-percentage").value

    console.log(`Calculating for: ${selectedCalculation}`)
    console.log(`Investment Value: R$ ${investmentValue}`)
    console.log(`Time Period: ${timePeriod} days`)
    console.log(`CDI Percentage: ${cdiPercentage}%`)

    // Here you would implement the specific calculation logic for each type
    performCalculation(selectedCalculation, investmentValue, timePeriod, cdiPercentage)
  })

  // Update market indicators
  updateMarketIndicators()
}

// Function to update market indicators
function updateMarketIndicators() {
  document.getElementById("cdi-rate").textContent = marketIndicators.cdi.rate
  document.getElementById("cdi-update").textContent = marketIndicators.cdi.lastUpdate
  document.getElementById("selic-rate").textContent = marketIndicators.selic.rate
  document.getElementById("selic-update").textContent = marketIndicators.selic.lastUpdate
}

// Function to perform calculations based on selected type
function performCalculation(type, value, period, cdiPercent) {
  // Placeholder for calculation logic
  switch (type) {
    case "CDB/RDB":
      console.log("Performing CDB/RDB calculation...")
      break
    case "LCI/LCA":
      console.log("Performing LCI/LCA calculation...")
      break
    case "Tesouro Direito":
      console.log("Performing Tesouro Direito calculation...")
      break
    default:
      console.log("Unknown calculation type")
  }
}

// Function to update market indicators (for future API integration)
function updateMarketData(newCdiRate, newSelicRate, updateDate) {
  marketIndicators.cdi.rate = newCdiRate
  marketIndicators.cdi.lastUpdate = updateDate
  marketIndicators.selic.rate = newSelicRate
  marketIndicators.selic.lastUpdate = updateDate

  updateMarketIndicators()
}

// Initialize the application when DOM is loaded
document.addEventListener("DOMContentLoaded", init)
