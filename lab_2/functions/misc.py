import pandas as pd 
import numpy as np 
import matplotlib.pyplot as plt 

from scipy.interpolate import interp1d

import QuantLib as ql

def find_prev_coupon_date(settlement_date, maturity_date, tenor, calendar, day_rolling):
    """ 
    Finds the last coupon date before the settlement date
    """

    schedule_unadj = ql.MakeSchedule(settlement_date,
                                     maturity_date,
                                     tenor)
    
    neg_tenor = ql.Period(-tenor.length(), tenor.units())
    previous_cpn_date = calendar.advance(schedule_unadj[1], neg_tenor, day_rolling)

    return previous_cpn_date

def set_scheduling_information(schedule, maturity_date, day_count, tenor, settlement_date, calendar, day_rolling):
    """ 
    Computes:
    - Accrual period
    - year_fracs: time passed between cash flows (in years)
    - payment_times: time passed between settlement date and cash flows (in years)

    Returns:
    - Dictionary containing information about: accrual period, year_fracs, payment_times, start date and pay date for each payment period with respect to each cash flow
    """

    coupon_dates = list(schedule)

    start_dates = coupon_dates[:-1]
    pay_dates = coupon_dates[1:]
    start_dates[0] = find_prev_coupon_date(settlement_date, maturity_date, tenor, calendar, day_rolling)

    day_count_time = ql.ActualActual(ql.ActualActual.ISDA)

    periods_pairings = list(zip(start_dates, pay_dates))

    year_fracs = [day_count.yearFraction(date[0], date[1]) for date in periods_pairings]
    payment_times = [day_count_time.yearFraction(settlement_date, pay_date) for pay_date in pay_dates]

    accrual_period = day_count.yearFraction(start_dates[0],settlement_date)

    return_dictionary = {
        "accrual_period": accrual_period,
        "year_fracs": year_fracs,
        "payment_times": payment_times,
        "start_dates": start_dates,
        "pay_dates": pay_dates
    }

    return return_dictionary

def set_discount_curve(curve, payment_times, input_discount = True):
    """ 
    Sets up the discount curve with respect to the appropriate payment times by interpolating the interest rate curve 
    """

    ### NOTE: redoit with the CubicSpline function from SciPy

    interpolation_kind = "linear"

    if input_discount == True:
   
        numerator_to_interpolate = -np.log(curve.values.reshape(-1))

        get_spot_rate = interp1d(
                    curve.index, 
                    numerator_to_interpolate, 
                    kind=interpolation_kind, 
                    fill_value="extrapolate"
                )

        interpolated_numerator = get_spot_rate(payment_times)
  
        discount_curve = np.exp(-interpolated_numerator)
    
    else:
        get_spot_rate = interp1d(
                    curve.index, 
                    curve.values.reshape(-1), 
                    kind=interpolation_kind, 
                    fill_value="extrapolate"
                )

        interpolated_rates = get_spot_rate(payment_times)
        discount_curve = np.exp(-interpolated_rates*payment_times)       

    return discount_curve