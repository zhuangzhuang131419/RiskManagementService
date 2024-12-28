export type OptionItem = {
    key: string;
    symbol: string;
}

export type OptionGreeksData = {
    delta: number;
    gamma: number;
    vega: number;
    theta: number;
    vanna_vs: number;
    vanna_sv: number;
    db: number;
    dkurt: number;
    position: number;
    bid: number;
    ask: number;
};

export type WingModelData = {
    atm_vol: number;
    v: number;
    k1: number;
    k2: number;
    b: number;
    atm_available: number
}

export type StrikePrices = {
    call_option: OptionGreeksData;
    put_option: OptionGreeksData;
}

export type GreeksResponse = {
    symbol: string;
    strike_prices: { [key: string]: StrikePrices };
}

export type CashGreeksResponse = {
    investor_id: string | null,
    delta: number | null,
    delta_cash: number | null,
    gamma_p_cash: number | null,
    vega_cash: number | null,
    theta_cash: number | null,
    db_cash: number | null,
    vanna_vs_cash: number | null,
    vanna_sv_cash: number | null,
    charm_cash: number | null
    underlying_price: number | null,
}
