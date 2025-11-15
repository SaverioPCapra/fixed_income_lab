from .coupon_bond import *
from .frn import *

import QuantLib as ql
import numpy as np
import pandas as pd

def summary_table_swap(input_dictionary_fixed,input_dictionary_float):
   
   return pd.merge(input_dictionary_fixed,input_dictionary_float, on="Start Date", how = "outer", suffixes=[" Fixed", " Floating"])

def price_swap(settlement_date, 
               maturity_date, 
               discount_curve, 
               calendar, 
               tenor_fixed_leg,
               tenor_floating_leg, 
               swap_rate,
               current_coupon_rate, 
               spread, 
               notional, 
               day_count_fixed_leg,
               day_count_floating_leg, 
               day_rolling, 
               schedule_fixed_leg,
               schedule_floating_leg,
               is_receiver = True):

    fixed_leg = price_coupon_bond(
        settlement_date,
        maturity_date,
        discount_curve,
        calendar,
        tenor_fixed_leg,
        swap_rate,
        notional,
        day_count_fixed_leg,
        day_rolling,
        schedule_fixed_leg        
    )

    floating_leg = price_floating_rate_note(
        settlement_date,
        maturity_date,
        discount_curve,
        calendar,
        tenor_floating_leg,
        current_coupon_rate,
        spread,
        notional,
        day_count_floating_leg,
        day_rolling,
        schedule_floating_leg
    )

    fixed_leg_discounted_cash_flows = fixed_leg["Discounted Coupons"]
    floating_leg_discounted_cash_flows = floating_leg["Discounted Coupons"]

    price = np.sum(floating_leg_discounted_cash_flows)-np.sum(fixed_leg_discounted_cash_flows)

    # The multiplier changes the sign of cash flows based on whether you're receiver or sender
    multiplier = 1

    if is_receiver == False:
            price = -price
            multiplier = -multiplier


    ##############
    floating_leg["Summary Table"]["Cash Flows"] = floating_leg["Coupons"]*multiplier
    floating_leg["Summary Table"]["Discounted Cash Flows"] = floating_leg["Discounted Coupons"]*multiplier

    fixed_leg["Summary Table"]["Cash Flows"] = -fixed_leg["Coupons"]*multiplier
    fixed_leg["Summary Table"]["Discounted Cash Flows"] = -fixed_leg["Discounted Coupons"]*multiplier

    summary_table = summary_table_swap(fixed_leg["Summary Table"],
                                       floating_leg["Summary Table"])

    #########

    return {
            "Price": price, 
            "Fixed Leg": fixed_leg, 
            "Floating Leg": floating_leg,
            "Summary Table": summary_table
            }