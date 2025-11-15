from .misc import *

def summary_table_frn(input_dictionary):

    start_dates = input_dictionary["start_dates"]
    pay_dates = input_dictionary["pay_dates"]
    year_fracs = input_dictionary["year_fracs"]
    payment_times = input_dictionary["payment_times"]
    discount_curve = input_dictionary["discount_curve"]
    cash_flows = input_dictionary["cash_flows"]
    discounted_cf = input_dictionary["discounted_cf"]

    spread = input_dictionary["spread"]
    coupon_rates = input_dictionary["coupon_rates_no_spread"]
    
    summary_dic = {
            "Start Date": start_dates,
            "Pay Date": pay_dates,
            "Year Frac": year_fracs,
            "Pay Time": payment_times,
            "Discount Curve": discount_curve,
            "Spread (bps)": spread,       
            "Coupon Rates (No Spread)": coupon_rates,
            "Cash Flows": cash_flows,
            "Discounted Cash Flows": discounted_cf,
    }

    summary = pd.DataFrame(summary_dic,
                            index = [i for i in range(1, len(start_dates)+1)] )
    
    return summary

def price_floating_rate_note(settlement_date, maturity_date, discount_curve, calendar, tenor, current_coupon_rate, spread, notional, day_count, day_rolling, schedule):

    scheduling_information = set_scheduling_information(schedule,
                                                        maturity_date,
                                                        day_count,
                                                        tenor,
                                                        settlement_date,
                                                        calendar,
                                                        day_rolling)

    accrual_period = scheduling_information["accrual_period"] 
    start_dates = scheduling_information["start_dates"]
    pay_dates = scheduling_information["pay_dates"]
    payment_times = scheduling_information["payment_times"]  
    accrued_interest = accrual_period*notional*current_coupon_rate

    payment_times = np.array(payment_times)
    
    year_fracs = scheduling_information["year_fracs"]  
    year_fracs = np.array(year_fracs)

    discount_curve = set_discount_curve(discount_curve, payment_times)
    spread_percentage = spread/10000

    coupon_rates = []

    for index in range(len(pay_dates)):
        
        tau_forward = year_fracs[index]

        if index == 0:
            coupon_rate = current_coupon_rate-spread_percentage
    
        else:
            df_start = discount_curve[index-1]
            df_end = discount_curve[index]
            
            forward_rate = 1/tau_forward * (df_start/df_end-1)

            coupon_rate = forward_rate
            
        coupon_rates.append(coupon_rate)

    
    coupon_rates = np.array(coupon_rates) + spread_percentage
    coupons = coupon_rates*notional*year_fracs

    cash_flows = coupons.copy()
    cash_flows[-1] += notional

    discounted_cash_flows = cash_flows*discount_curve

    dirty_price = np.sum(discounted_cash_flows)
    clean_price = dirty_price - accrued_interest
    
    ### Prepare Table

    input_dictionary = {
        "start_dates": start_dates,
        "pay_dates": pay_dates,
        "year_fracs": year_fracs,
        "payment_times": payment_times,
        "discount_curve": discount_curve,
        "cash_flows": cash_flows,
        "discounted_cf": discounted_cash_flows,
        "spread": spread,
        "coupon_rates_no_spread": coupon_rates-spread_percentage
        }

    summary_table = summary_table_frn(input_dictionary)

    return {"Dirty Price": dirty_price, 
            "Accrued Interest": accrued_interest, 
            "Clean Price": clean_price, 
            "Discounted Coupons": coupons*discount_curve,
            "Summary Table": summary_table}    