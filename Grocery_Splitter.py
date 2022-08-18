###imports
import pandas as pd
import numpy as np

def split_groceries(grocery_bill='Grocery_Bill.csv'):
    ###import csv (has to be formatted correctly — first column 'Item_Cost', followed by a column for each person)
    bill = pd.read_csv(grocery_bill)

    ###calculate the cost per item
    bill['Cost_Per_Person'] = bill['Item_Cost'] / (bill.count(axis=1) - 1)

    ###calculate the cost per person based on the costs per item
    def get_costs(li):
        costs = []
        for i in li:
            cost = bill.groupby(i).sum().Cost_Per_Person[0]
            costs.append(cost)
        return costs
    even_split = pd.DataFrame({'Person':bill.columns[1:-1],'Even_Cost':get_costs(bill.columns[1:-1])})

    ###Receive input on how much each person eats
    amounts = []
    for i in even_split.Person:
        amount = input('How much does ' + i + ' eat? (Small, Medium, or Large) ').capitalize()
        amounts.append(amount)
    even_split['Amount'] = amounts

    ###calculate the total amount of money spent in the bill
    total = even_split.Even_Cost.sum()

    ###create arrays of potential modifier amounts, ensuring that people who eat more have larger modifiers than those who eat less
    large_percentages = np.arange(1.000, 1.300, .005)
    medium_percentages = np.arange(.800, 1.000, .005)
    small_percentages = np.arange(.700, .800, .005)

    ###iterate through each combination of the above modifier arrays to see which modifiers can be used to reach the total cost of the bill
    large_numbers = []
    medium_numbers = []
    small_numbers = []
    modified_totals = []

    large_total = even_split[even_split.Amount == 'Large'].groupby('Amount').sum().Even_Cost[0]
    medium_total = even_split[even_split.Amount == 'Medium'].groupby('Amount').sum().Even_Cost[0]
    small_total = even_split[even_split.Amount == 'Small'].groupby('Amount').sum().Even_Cost[0]

    for i in large_percentages:
        large_modified = large_total * i
        for j in medium_percentages:
            medium_modified = medium_total * j
            for l in small_percentages:
                small_modified = small_total * l
            
                modified_total = large_modified + medium_modified + small_modified
                modified_totals.append(modified_total)
                large_numbers.append(i)
                medium_numbers.append(j)
                small_numbers.append(l)
        
    distances = abs(total-modified_totals)

    ###calculate how much of an imbalance in pay each modifier combination creates (this then allows the user later to select ratios between large, medium, and small that best reflect how much the different people paying the bill eat
    multipliers = np.array(large_numbers) / np.array(medium_numbers)
    
    multipliers2 = np.array(large_numbers) / np.array(small_numbers)
    
    multipliers3 = np.array(medium_numbers) / np.array(small_numbers)

###create a table that allows the user to examine the 20 best (in terms of distance from total) modifiers, and then select their preferred modifiers
    d = {'Large_Modifier':large_numbers, 'Medium_Modifier':medium_numbers, 'Small_Modifier':small_numbers, 'Modified_Totals':modified_totals, 'Absolute_Distance':distances, 'Large:Medium':multipliers, 'Large:Small':multipliers2, 'Medium:Small':multipliers3}
    Pareto_Table = pd.DataFrame(data=d)
    selection = Pareto_Table[(Pareto_Table.Absolute_Distance < .01)].sort_values(['Absolute_Distance']).head(20).reset_index().drop(['index', 'Absolute_Distance', 'Modified_Totals'], axis=1)
    print(selection)

    select = int(input('Select which modifiers to use to split the grocery bill by inputting the index of your preferred row: '))

    ###create a final cost table that shows how much each person would pay evenly, how much they eat, what their modifier is, and how much they pay after modifiers
    modifiers = selection.iloc[select][0:3]
    modifiers

    even_split['Modifier'] = even_split.Amount.map({'Large': modifiers[0], 'Medium': modifiers[1], 'Small': modifiers[2]})
    even_split['Modified_Cost'] = even_split.Even_Cost * even_split.Modifier
    final_cost = even_split
    print(final_cost)

split_groceries()