from .misc import *

import QuantLib as ql
import numpy as np
import pandas as pd

def summary_table_couponbond(input_dictionary):
    """ 
    Returns a summary table containing the relevant information about 
    """ 

    start_dates = input_dictionary["start_dates"]
    pay_dates = input_dictionary["pay_dates"]
    year_fracs = input_dictionary["year_fracs"]
    payment_times = input_dictionary["payment_times"]
    discount_curve = input_dictionary["discount_curve"]
    cash_flows = input_dictionary["cash_flows"]
    discounted_cf = input_dictionary["discounted_cf"]
   
    summary_dic = {
            "Start Date": start_dates,
            "Pay Date": pay_dates,
            "Year Frac": year_fracs,
            "Pay Time": payment_times,
            "Discount Curve": discount_curve,
            "Cash Flows": cash_flows,
            "Discounted Cash Flows": discounted_cf,
    }

    summary = pd.DataFrame(summary_dic,
                            index = [i for i in range(1, len(start_dates)+1)] )
    
    return summary

def price_coupon_bond(settlement_date, maturity_date, discount_curve, calendar, tenor, coupon_rate, notional, day_count, day_rolling, schedule, input_discount = True):

    scheduling_information = set_scheduling_information(schedule,
                                                        maturity_date,
                                                        day_count,
                                                        tenor,
                                                        settlement_date,
                                                        calendar,
                                                        day_rolling)

    accrual_period = scheduling_information["accrual_period"] 

    payment_times = scheduling_information["payment_times"]  
    payment_times = np.array(payment_times)
    
    year_fracs = scheduling_information["year_fracs"]  
    year_fracs = np.array(year_fracs)

    discount_curve = set_discount_curve(discount_curve, payment_times, input_discount)

    coupons = notional*coupon_rate*year_fracs
    accrued_interest = accrual_period*notional*coupon_rate

    cash_flows = coupons.copy()
    cash_flows[-1] += notional

    discounted_cash_flows = cash_flows*discount_curve

    dirty_price = np.sum(discounted_cash_flows)
    clean_price = dirty_price - accrued_interest


    ### Prepare Table
 
    start_dates = scheduling_information["start_dates"]
    pay_dates = scheduling_information["pay_dates"]

    input_dictionary = {
        "start_dates": start_dates,
        "pay_dates": pay_dates,
        "year_fracs": year_fracs,
        "payment_times": payment_times,
        "discount_curve": discount_curve,
        "cash_flows": cash_flows,
        "discounted_cf": discounted_cash_flows,
        "discounted_coupons": coupons*discount_curve
    }

    summary_table = summary_table_couponbond(input_dictionary)

    return {"Dirty Price": dirty_price, 
            "Accrued Interest": accrued_interest, 
            "Clean Price": clean_price, 
            "Discounted Coupons": coupons*discount_curve,
            "Summary Table": summary_table}    