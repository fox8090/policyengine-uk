from openfisca_uk.model_api import *


class lbtt_on_residential_property(Variable):
    label = "Land and Buildings Transaction Tax on residential property"
    documentation = (
        "Tax charge from purchase or rental of residential property"
    )
    entity = Household
    definition_period = YEAR
    value_type = float
    unit = "currency-GBP"

    def formula(household, period, parameters):
        lbtt = parameters(period).revenue_scotland.lbtt
        # Tax on main-home purchases
        price = household("main_residential_property_purchased", period)
        residential_purchase_qualifies_as_first_buy = household(
            "main_residential_property_purchased_is_first_home", period
        )
        main_residential_purchase_tax = where(
            residential_purchase_qualifies_as_first_buy,
            lbtt.residential.first_time_buyer_rate.calc(price),
            lbtt.residential.rate.calc(price),
        )
        # Tax on second-home purchases
        second_home_price = household(
            "additional_residential_property_purchased", period
        )
        additional_residential_purchase_tax = lbtt.residential.rate.calc(
            second_home_price
        ) + (
            lbtt.residential.additional_residence_surcharge * second_home_price
        )
        # Tax on residential rents
        cumulative_rent = household("cumulative_residential_rent", period)
        rent = household("rent", period)
        residential_rent_tax = lbtt.rent.calc(
            cumulative_rent + rent
        ) - lbtt.rent.calc(cumulative_rent)
        return household("lbtt_liable", period) * (
            main_residential_purchase_tax
            + additional_residential_purchase_tax
            + residential_rent_tax
        )


class lbtt_on_non_residential_property(Variable):
    label = "LBTT on non-residential property"
    documentation = (
        "Tax charge from purchase or rental of non-residential property"
    )
    entity = Household
    definition_period = YEAR
    value_type = float
    unit = "currency-GBP"

    def formula(household, period, parameters):
        lbtt = parameters(period).revenue_scotland.lbtt
        # Tax on non-residential purchases
        price = household("non_residential_property_purchased", period)
        non_residential_purchase_tax = lbtt.non_residential.calc(price)
        # Tax on non-residential rents
        cumulative_rent = household("cumulative_non_residential_rent", period)
        rent = household("non_residential_rent", period)
        non_residential_rent_tax = lbtt.rent.calc(
            cumulative_rent + rent
        ) - lbtt.rent.calc(cumulative_rent)
        return household("lbtt_liable", period) * (
            non_residential_purchase_tax + non_residential_rent_tax
        )


class lbtt_liable(Variable):
    label = "Liable for Land and Buildings Transaction Tax"
    documentation = "Whether the household is liable for Land and Buildings Transaction Tax"
    entity = Household
    definition_period = YEAR
    value_type = bool
    unit = "currency-GBP"

    def formula(household, period):
        country = household("country", period)
        countries = country.possible_values
        return country == countries.SCOTLAND


class land_and_buildings_transaction_tax(Variable):
    label = "Land and Buildings Transaction Tax"
    documentation = "Total tax liability for Scotland's LBTT"
    entity = Household
    definition_period = YEAR
    value_type = float
    unit = "currency-GBP"

    def formula(household, period):
        return add(
            household,
            period,
            [
                "lbtt_on_residential_property",
                "lbtt_on_non_residential_property",
            ],
        )


class expected_lbtt(Variable):
    label = "Land and Buildings Transaction Tax (expected)"
    documentation = "Expected value of LBTT"
    entity = Household
    definition_period = YEAR
    value_type = float
    unit = "currency-GBP"

    def formula(household, period):
        return household.state("property_sale_rate", period) * household(
            "land_and_buildings_transaction_tax", period
        )