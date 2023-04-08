// Draw a XY graph which compares 2 types of health insurance plans: gHIP and PPO. The X axis stands for your medical expense, and Y axis for personal cost.
// Internal parameters should be the cost of each plan, the deductible of each plan, and the maximum out-of-pocket cost of each plan, also one of the plan get a contribution from the company, so we need to take that into consideration.

// gHIP parameters of cost, contribution, deductible, and maximum out-of-pocket cost
gHIP_cost = 0;
gHIP_contribution = 1000;
gHIP_deductible = 1500;
gHIP_out_of_pocket_max = 2600;
gHIP_coinsurance = 0.1;
// PPO parameters of cost, contribution, deductible, and maximum out-of-pocket cost
PPO_cost = 1506;
PPO_contribution = 0;
PPO_deductible = 400;
PPO_out_of_pocket_max = 2000;
PPO_coinsurance = 0.1;

// The X axis stands for your original medical expense, and Y axis for actual personal cost.
// For example, when the medical expense is 0, the personal cost of gHIP is 0 - gHIP_contribution = -1000, and the actual personal cost of PPO is 1506.
// When the medical expense is 1500, the personal cost of gHIP is 1500 - gHIP_contribution = 500, and the personal cost of PPO is 1506 + 400 + (1500 - 400) * PPO_coinsurance = 1506 + 400 + 1100 * 0.1 = 2506.
// When the medical expense is 2500, the personal cost of gHIP is 1500 + (2500 - 1500) * gHIP_coinsurance - gHIP_contribution = 1500 + 1000 * 0.1 - 1000 = 1600, and the personal cost of PPO is 1506 + 400 + (2500 - 400) * PPO_coinsurance = 1506 + 400 + 2100 * 0.1 = 3506.
// When the medical expense is 10000, the personal cost of gHIP is 1500 + (10000 - 1500) * gHIP_coinsurance - gHIP_contribution = 1500 + 8500 * 0.1 - 1000 = 1350, and the personal cost of PPO is 1506 + 400 + (10000 - 400) * PPO_coinsurance = 1506 + 400 + 9600 * 0.1 = 2866.
// When the medical expense is 30000, both plans reach the out-of-pocket-maximum. The personal cost of gHIP is 2600 - gHIP_contribution = 1600, and the personal cost of PPO is 1506 + 2000 = 3506.

// The following code is to draw the XY graph.
// The X axis stands for your original medical expense, and Y axis for actual personal cost.
// The X axis is from 0 to 50000, and the Y axis is from 0 to 5000.
// The X axis is divided into 500 parts, and the Y axis is divided into 100 parts.

// Customize the resolution of graph. The default resolution has 1000 parts on X axis and 100 parts on Y axis, and each part is 100 units, so the X axis is from 0 to 1000000.
NUM_DATA_POINTS = 1000;
DISTANCE_PER_DATA_POINT = 100;
x_medical_expense = [], y_gHIP_personal_cost = [], y_PPO_personal_cost = [];

for (let i = 0; i < NUM_DATA_POINTS; i++) {
    x_medical_expense[i] = i * DISTANCE_PER_DATA_POINT;
    y_gHIP_personal_cost[i] = 0;
    y_PPO_personal_cost[i] = 0;
}

for (let i = 0; i < x_medical_expense.length; i++) {
    gHIP_out_of_pocket_cost = 0;
    // if the medical expense is less than the deductible, the personal cost is the medical expense - the contribution
    if (x_medical_expense[i] <= gHIP_deductible) {
        y_gHIP_personal_cost[i] = x_medical_expense[i] - gHIP_contribution;
        gHIP_out_of_pocket_cost = x_medical_expense[i];
    } else {
        y_gHIP_personal_cost[i] = gHIP_deductible - gHIP_contribution + (x_medical_expense[i] - gHIP_deductible) * gHIP_coinsurance;
        gHIP_out_of_pocket_cost = gHIP_deductible + (x_medical_expense[i] - gHIP_deductible) * gHIP_coinsurance;
        // if the out-of-pocket cost is more than the maximum out-of-pocket cost, the personal cost is the maximum out-of-pocket cost - the contribution
        if (gHIP_out_of_pocket_cost >= gHIP_out_of_pocket_max) {
            y_gHIP_personal_cost[i] = gHIP_out_of_pocket_max - gHIP_contribution;
        }
    }

    PPO_out_of_pocket_cost = 0;
    // if the medical expense is less than the deductible, the personal cost is the cost + the medical expense
    if (x_medical_expense[i] <= PPO_deductible) {
        y_PPO_personal_cost[i] = PPO_cost + x_medical_expense[i];
    } else {
        y_PPO_personal_cost[i] = PPO_cost + PPO_deductible + (x_medical_expense[i] - PPO_deductible) * PPO_coinsurance;
        PPO_out_of_pocket_cost = PPO_deductible + (x_medical_expense[i] - PPO_deductible) * PPO_coinsurance;
        // if the out-of-pocket cost is more than the maximum out-of-pocket cost, the personal cost is the cost + the maximum out-of-pocket cost
        if (PPO_out_of_pocket_cost >= PPO_out_of_pocket_max) {
            y_PPO_personal_cost[i] = PPO_cost + PPO_out_of_pocket_max;
        }
    }
}

// Use Plotly to draw the XY graph.
var trace1 = {
    x: x_medical_expense,
    y: y_gHIP_personal_cost,
    mode: 'lines+markers',
    name: 'gHIP'
  };
  
var trace2 = {
x: x_medical_expense,
y: y_PPO_personal_cost,
mode: 'lines+markers',
name: 'PPO'
};

data = [trace1, trace2];

// Draw the XY graph.
Plotly.newPlot('myDiv', data);