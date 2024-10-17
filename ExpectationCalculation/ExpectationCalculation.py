from collections import defaultdict

# 定义卷轴类
class Scroll:
    def __init__(self, name, success_rate, cost, attribute_increase, destroy_rate=0):
        self.name = name  # 卷轴的名称
        self.success_rate = success_rate
        self.cost = cost
        self.attribute_increase = attribute_increase
        self.destroy_rate = destroy_rate
    
class Item:
    def __init__(self, name, initial_attribute, cost, upgrade_slots):
        self.name = name  # 卷轴的名称
        self.initial_attribute = initial_attribute
        self.cost = cost
        self.upgrade_slots = upgrade_slots

# 遍历所有砸卷的可能组合并记录结果及概率
# current_attribute: 当前attribute的值，0代表道具消失
# scroll_path: 砸卷的过程记录
# scroll_result: 砸卷的结果记录
# attribute_results: 砸卷结果按最终攻击统计
# scroll_results: 砸卷结果按砸卷组合统计
def calculate_outcome(current_attribute, remaining_slots, item_disappeared, cost, probability, available_scrolls, scroll_path, scroll_result, attribute_results, scroll_results):
    # 在剩余次数为0时终止
    if remaining_slots == 0:
        # 将结果按最终攻击保存
        attribute_results[current_attribute][tuple(scroll_path)].append((current_attribute, scroll_result, cost, probability))
        # 将结果按卷轴组合保存
        scroll_results[tuple(scroll_path)].append((current_attribute, scroll_result, cost, probability))
        return

    for scroll in available_scrolls:
        # 如果道具已消失
        if item_disappeared:
            calculate_outcome(0, remaining_slots - 1, item_disappeared, cost, probability, available_scrolls, scroll_path + [scroll.name], scroll_result + [scroll.name + " (道具已消失）"], attribute_results, scroll_results)
        # 正常砸卷
        else:
            # 成功的情况
            calculate_outcome(current_attribute + scroll.attribute_increase, remaining_slots - 1, item_disappeared, cost + scroll.cost, probability * scroll.success_rate, available_scrolls, scroll_path + [scroll.name], scroll_result + [scroll.name + " (成功）"], attribute_results, scroll_results)
            # 失败的情况
            if scroll.destroy_rate > 0:
                # 失败且道具消失
                calculate_outcome(0, remaining_slots - 1, True, cost + scroll.cost, probability * (1 - scroll.success_rate) * scroll.destroy_rate, available_scrolls, scroll_path + [scroll.name], scroll_result + [scroll.name + " (失败, 道具消失)"], attribute_results, scroll_results)
                # 失败但道具保留
                calculate_outcome(current_attribute, remaining_slots - 1, item_disappeared, cost + scroll.cost, probability * (1 - scroll.success_rate) * (1 - scroll.destroy_rate), available_scrolls, scroll_path + [scroll.name], scroll_result + [scroll.name + " (失败, 道具保留)"], attribute_results, scroll_results)
            else:
                # 道具不会消失，只是失败
                calculate_outcome(current_attribute, remaining_slots - 1, item_disappeared, cost + scroll.cost, probability * (1 - scroll.success_rate), available_scrolls, scroll_path + [scroll.name], scroll_result + [scroll.name + " (失败)"], attribute_results, scroll_results)

# 计算期望收益的函数
def calculate_expected_profit(results, market_prices):
    combination_profits = defaultdict(lambda: defaultdict(lambda: defaultdict(float)))

    for scroll_path, outcomes in results.items():
        profit_expectation = 0.0
        for outcome in outcomes:
            attribute, scroll_result, cost, probability = outcome
            market_price = market_prices.get(attribute, 0)
            profit = market_price - cost
            combination_profits[scroll_path][tuple(scroll_result)]['attribute'] = attribute
            combination_profits[scroll_path][tuple(scroll_result)]['probability'] = probability
            combination_profits[scroll_path][tuple(scroll_result)]['cost'] = cost
            combination_profits[scroll_path][tuple(scroll_result)]['market_price'] = market_price
            combination_profits[scroll_path][tuple(scroll_result)]['profit'] = profit
            profit_expectation += probability * profit
        combination_profits[scroll_path]['profit_expectation'] = profit_expectation

    return combination_profits

# 打印期望收益的细节
def print_expected_profit_details(results, market_prices, print_details):
    combination_profits = calculate_expected_profit(results, market_prices)

    # Convert dictionary to a sorted list of tuples based on 'profit_expectation'
    sorted_combinations = sorted(combination_profits.items(), key=lambda x: x[1]['profit_expectation'], reverse=True)

    MAX_COMBINATION = 2
    i = 0
    for scroll_path, scroll_result_with_details in sorted_combinations:
        print(f"{' + '.join(scroll_path)}, 预期收益为: {scroll_result_with_details['profit_expectation']:.2f}")
        for scroll_result, details in scroll_result_with_details.items():
            if scroll_result == 'profit_expectation':
                continue
            attribute = details['attribute']
            probability = details['probability']
            cost = details['cost']
            market_price = details['market_price']
            profit = details['profit']
            # 打印每种scroll_path详细的scroll_result及其概率
            if (print_details):
                print(f" {' + '.join(scroll_result)}, 数值{attribute}，概率: {probability * 100:.2f}%，成本: {cost}，市场价格: {market_price}，收益: {profit:.2f}")
        i += 1
        if (i >= MAX_COMBINATION):
            break
        print()

# 主函数
def main(item_prices, target_attribute=None, print_details=False):
    market_prices, available_scrolls, available_items = item_prices
    
    # 开始计算
    for item in available_items:
        combination_profits = defaultdict(lambda: defaultdict(lambda: defaultdict(float)))
        attribute_results = defaultdict(lambda: defaultdict(list))
        scroll_results = defaultdict(list)
        calculate_outcome(item.initial_attribute, item.upgrade_slots, False, item.cost, 1.0, available_scrolls, [], [], attribute_results, scroll_results)

        print('道具名: ' + item.name)
        print('初始数值: ' + f" {item.initial_attribute}")
        print('道具成本: ' + f" {item.cost}")
        print('-------------------------------------------------------------')
        # 先输出目标数值的卷轴组合
        if target_attribute:
            if target_attribute in attribute_results:
                print(f"达到{target_attribute}数值的卷轴组合：")
                print_expected_profit_details(attribute_results[target_attribute], market_prices)
            else:
                print(f"无法达到{target_attribute}数值。\n")
            print()

        # 输出所有数值的卷轴组合
        # for attribute in sorted(attribute_results.keys()):
        #     print(f"{attribute}数值：")
        #     # 按期望总成本排序
        #     sorted_outcomes = sorted(attribute_results[attribute], key=lambda x: x[1] / x[2] if x[2] > 0 else float('inf'))
        #     for outcome in sorted_outcomes:
        #         scroll_path, cost, probability = outcome
        #         expected_total_cost = cost / probability if probability > 0 else float('inf')
        #         print(f"{' + '.join(scroll_path)}：总成本: {cost}，概率: {probability * 100:.2f}%，期望总成本: {expected_total_cost:.2f}")
        #     print()

        # 计算和输出各个卷轴组合的期望收益
        if market_prices:
            print("各个卷轴组合的期望收益：")
            print_expected_profit_details(scroll_results, market_prices, print_details)
        print('-------------------------------------------------------------')

if __name__ == "__main__":
    # 设置目标数值和市场价格
    target_attribute = None

    # 装备胚子的价格
    # 短刀
    knife_items = [
        # 胚子
        # Item('龙牙', initial_attribute = 101, cost = 66, upgrade_slots = 7), # 预期2216，先砸10卷
        # Item('龙牙', initial_attribute = 102, cost = 177, upgrade_slots = 7), # 预期4381，先砸10卷
        # Item('龙牙', initial_attribute = 103, cost = 488, upgrade_slots = 7), # 预期9011，先砸10卷
        # Item('龙牙', initial_attribute = 104, cost = 1188, upgrade_slots = 7), # 预期13255，先砸10卷
        # Item('龙牙', initial_attribute = 105, cost = 2888, upgrade_slots = 7), # 预期5007
        # Item('龙牙', initial_attribute = 106, cost = 6666, upgrade_slots = 7), # 预期7231
        # Item('龙牙', initial_attribute = 107, cost = 16000, upgrade_slots = 7), # 预期7135
        # Item('龙牙', initial_attribute = 108, cost = 22222, upgrade_slots = 7), # 预期7290
        # Item('龙牙', initial_attribute = 109, cost = 34500, upgrade_slots = 7), # 预期7130
        # Item('龙牙', initial_attribute = 110, cost = 51750, upgrade_slots = 7), # 预期7459，750R
        # 砸过
        # Item('龙牙', initial_attribute = 106, cost = 3200, upgrade_slots = 6), # 预期1638，101胚子99
        # Item('龙牙', initial_attribute = 111, cost = 4000, upgrade_slots = 6), # 预期4381，102胚子177
        # Item('龙牙', initial_attribute = 108, cost = 7100, upgrade_slots = 6), # 预期9011，103胚子488
        # Item('龙牙', initial_attribute = 109, cost = 14000, upgrade_slots = 6), # 预期13255, 104胚子1188
        # Item('龙牙', initial_attribute = 119, cost = 136000, upgrade_slots = 3), # 预期-18170
    ]

    # 卷轴名称，成功率，成本，增加数值，失败后道具消失概率
    # 短刀 - Updated 08/25/2024
    knife_scrolls = [
        Scroll("10%卷轴", 0.11, 220, 5),   # 10%成功几率的卷轴
        Scroll("60%卷轴", 0.66, 2, 2),    # 60%成功几率的卷轴
        Scroll("30%卷轴", 0.33, 6000, 5, 0.5),  # 30%成功几率的卷轴，失败后有50%几率道具消失
        Scroll("70%卷轴", 0.77, 20, 2, 0.5)  # 70%成功几率的卷轴，失败后有50%几率道具消失
    ]

    # Updated 09/01/2024
    knife_market_prices = {
        110: 0,
        114: 70,
        115: 222,
        116: 777,
        117: 4000,
        118: 9999,
        119: 22222,
        120: 42000, # ~600R
        121: 63000, # ~900R
        122: 91000, # ~1300R
        123: 131000, # ~1900R
        124: 168000, # ~2400R
        125: 210800, # ~3100R
        126: 280000, # ~4000R
        127: 364000, # ~5200R
        128: 476000, # ~6800R
        129: 700000, # ~10000R
        130: 884000, # ~13000R
        131: 1050000, # ~15000R
        132: 1050000, # ~15000R
        133: 1050000, # ~15000R
        134: 1050000, # ~15000R
    }

    knife_prices = [
        knife_market_prices,
        knife_scrolls,
        knife_items
    ]

    # 卷轴名称，成功率，成本，增加数值，失败后道具消失概率
    # 弓 - Updated 08/25/2024
    bow_items = [
        # 胚子
        # Item('金龙', initial_attribute = 101, cost = 60, upgrade_slots = 7), # 预期-147
        # Item('金龙', initial_attribute = 102, cost = 150, upgrade_slots = 7), #预期 547
        # Item('金龙', initial_attribute = 103, cost = 666, upgrade_slots = 7), # 预期365
        # Item('金龙', initial_attribute = 104, cost = 1555, upgrade_slots = 7), # 预期5470
        # Item('金龙', initial_attribute = 105, cost = 4666, upgrade_slots = 7), # 预期9585
        # Item('金龙', initial_attribute = 106, cost = 8555, upgrade_slots = 7), # 预期13442，最低8000w卖过
        # Item('金龙', initial_attribute = 107, cost = 16000, upgrade_slots = 7),
        # Item('金龙', initial_attribute = 108, cost = 26666, upgrade_slots = 7),
        # Item('金龙', initial_attribute = 109, cost = 66666, upgrade_slots = 7)
        # Item('金龙', initial_attribute = 110, cost = 46920, upgrade_slots = 7),
        # 砸过
        # Item('金龙', initial_attribute = 106, cost = 4700, upgrade_slots = 6), # 预期5560，胚子101=60
        # Item('金龙', initial_attribute = 107, cost = 5600, upgrade_slots = 6), # 预期8588，胚子102=150
        # Item('金龙', initial_attribute = 108, cost = 10700, upgrade_slots = 6), # 预期17286，胚子103=666
        # Item('金龙', initial_attribute = 109, cost = 19600, upgrade_slots = 6), # 预期25852，胚子104=1555
        Item('金龙', initial_attribute = 116, cost = 140000, upgrade_slots = 5), 
    ]
    bow_scrolls = [
        Scroll("10%卷轴", 0.11, 410, 5),   # 10%成功几率的卷轴
        Scroll("60%卷轴", 0.66, 20, 2),    # 60%成功几率的卷轴
        Scroll("30%卷轴", 0.33, 10500, 5, 0.5),  # 30%成功几率的卷轴，失败后有50%几率道具消失
        Scroll("70%卷轴", 0.77, 40, 2, 0.5)  # 30%成功几率的卷轴，失败后有50%几率道具消失
    ]
    bow_market_prices = {
        110: 0,
        114: 70,
        115: 222,
        116: 3000,
        117: 7000,
        119: 40000,
        120: 59500, # ~850R
        121: 77000, # ~1100R
        122: 101500, # ~1450R
        123: 140000, # ~2000R
        124: 241500, # ~3500R
        125: 420000, # ~6000R
        126: 517500, # ~9000R
        127: 770000, # ~11000R
        128: 910000, # ~13000R
        129: 1120000, # ~16000R
        130: 1400000, # ~20000R
        131: 1400000, # ~20000R
        132: 1400000, # ~20000R
        133: 1400000, # ~20000R
        134: 1400000, # ~20000R
    }
    bow_prices = [
        bow_market_prices,
        bow_scrolls,
        bow_items
    ]

    glove_items = [
        Item('褐手6次', initial_attribute = 0, cost = 199, upgrade_slots = 6),
        Item('褐手7次', initial_attribute = 0, cost = 3670, upgrade_slots = 7),
    ]
    # 卷轴名称，成功率，成本，增加数值，失败后道具消失概率
    # 褐手 - Updated 09/01/2024
    glove_scrolls = [
        Scroll("10%卷轴", 0.11, 35, 3),   # 10%成功几率的卷轴
        Scroll("60%卷轴", 0.66, 840, 2),    # 60%成功几率的卷轴
        Scroll("30%卷轴", 0.33, 12000, 3, 0.5),  # 30%成功几率的卷轴，失败后有50%几率道具消失
        Scroll("70%卷轴", 0.77, 2700, 2, 0.5)  # 30%成功几率的卷轴，失败后有50%几率道具消失
    ]
    # Updated 09/02/2024
    glove_market_prices = {
        6: 198,
        7: 400,
        8: 600,
        9: 1000,
        10: 1444,
        12: 6000,
        13: 21000, # ~300R
        14: 58650, # ~850R
        15: 151800, # ~2200R
        16: 414000, # ~6000R
        17: 1104000 # ~16000R
    }
    glove_prices = [
        glove_market_prices,
        glove_scrolls,
        glove_items
    ]

    main(item_prices=knife_prices, target_attribute=target_attribute, print_details=False)