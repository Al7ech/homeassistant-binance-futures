"""
Binance exchange sensor
"""

from homeassistant.const import ATTR_ATTRIBUTION
from homeassistant.components.sensor import SensorEntity

CURRENCY_ICONS = {
    "BTC": "mdi:currency-btc",
    "ETH": "mdi:currency-eth",
    "EUR": "mdi:currency-eur",
    "LTC": "mdi:litecoin",
    "USD": "mdi:currency-usd",
}

QUOTE_ASSETS = ["USD", "BTC", "USDT", "BUSD", "USDC"]

DEFAULT_COIN_ICON = "mdi:currency-usd-circle"

ATTRIBUTION = "Data provided by Binance"
ATTR_WALLET_BALANCE = "wallet_balance"
ATTR_UNREALIZED_PROFIT = "unrealized_pnl"
ATTR_MARGIN_BALANCE = "margin_balance"
ATTR_NATIVE_BALANCE = "native_balance"
ATTR_SYMBOL = "symbol"
ATTR_POSITION_AMOUNT = "position_amount"

DATA_BINANCE = "binance_cache"


def setup_platform(hass, config, add_entities, discovery_info=None):
    """Setup the Binance sensors."""

    if discovery_info is None:
        return
    if all(i in discovery_info for i in ["name", "asset", "walletBalance", "unrealizedProfit", "marginBalance"]):
        name = discovery_info["name"]
        asset = discovery_info["asset"]
        wallet_balance = discovery_info["walletBalance"]
        unrealized_profit = discovery_info["unrealizedProfit"]
        margin_balance = discovery_info["marginBalance"]
        native = discovery_info["native"]

        sensor = BinanceSensor(
            hass.data[DATA_BINANCE], name, asset, wallet_balance, unrealized_profit, margin_balance, native
        )
    elif all(i in discovery_info for i in ["name", "symbol", "positionAmt", "unrealizedProfit"]):
        name = discovery_info["name"]
        symbol = discovery_info["symbol"]
        position_amount = discovery_info["positionAmt"]
        unrealized_profit = discovery_info["unrealizedProfit"]
        native = discovery_info["native"]

        sensor = BinancePositionSensor(
            hass.data[DATA_BINANCE], name, symbol, position_amount, unrealized_profit, native
        )
    elif all(i in discovery_info for i in ["name", "symbol", "price"]):
        name = discovery_info["name"]
        symbol = discovery_info["symbol"]
        price = discovery_info["price"]

        sensor = BinanceExchangeSensor(hass.data[DATA_BINANCE], name, symbol, price)

    add_entities([sensor], True)


class BinanceSensor(SensorEntity):
    """Representation of a Sensor."""

    def __init__(self, binance_data, name, asset, wallet_balance, unrealized_profit, margin_balance, native):
        """Initialize the sensor."""
        self._binance_data = binance_data
        self._name = f"{name} {asset} Balance"
        self._asset = asset
        self._wallet_balance = wallet_balance
        self._unrealized_profit = unrealized_profit
        self._margin_balance = margin_balance
        self._native = native
        self._unit_of_measurement = asset
        self._state = None
        self._native_balance = None

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement this sensor expresses itself in."""
        return self._unit_of_measurement

    @property
    def icon(self):
        """Icon to use in the frontend, if any."""
        return CURRENCY_ICONS.get(self._asset, DEFAULT_COIN_ICON)

    @property
    def extra_state_attributes(self):
        """Return the state attributes of the sensor."""

        return {
            ATTR_ATTRIBUTION: ATTRIBUTION,
            ATTR_NATIVE_BALANCE: f"{self._native_balance} {self._native}",
            ATTR_WALLET_BALANCE: f"{self._wallet_balance} {self._unit_of_measurement}",
            ATTR_UNREALIZED_PROFIT: f"{self._unrealized_profit} {self._unit_of_measurement}",
            ATTR_MARGIN_BALANCE: f"{self._margin_balance} {self._unit_of_measurement}"
        }

    def update(self):
        """Update current values."""
        self._binance_data.update()
        for balance in self._binance_data.balances:
            if balance["asset"] == self._asset:
                self._state = balance["walletBalance"]
                self._wallet_balance = balance["walletBalance"]
                self._unrealized_profit = balance["unrealizedProfit"]
                self._margin_balance = balance["marginBalance"]

                if balance["asset"] == self._native:
                    self._native_balance = round(float(balance["walletBalance"]), 2)
                break

class BinancePositionSensor(SensorEntity):
    """Representation of a Sensor."""
    def __init__(self, binance_data, name, symbol, position_amount, unrealized_profit, native):
        """Initialize the sensor."""
        self._binance_data = binance_data
        self._name = f"{name} {symbol} Position"
        self._symbol = symbol
        self._position_amount = position_amount
        self._unrealized_profit = unrealized_profit
        self._native = native
        self._unit_of_measurement = symbol
        self._state = None
        self._native_balance = None

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement this sensor expresses itself in."""
        return self._unit_of_measurement

    @property
    def icon(self):
        """Icon to use in the frontend, if any."""
        return CURRENCY_ICONS.get(self._symbol[:3], DEFAULT_COIN_ICON)

    @property
    def extra_state_attributes(self):
        """Return the state attributes of the sensor."""

        return {
            ATTR_ATTRIBUTION: ATTRIBUTION,
            ATTR_NATIVE_BALANCE: f"{self._native_balance} {self._native}",
            ATTR_POSITION_AMOUNT: f"{self._position_amount} {self._unit_of_measurement}",
            ATTR_UNREALIZED_PROFIT: f"{self._unrealized_profit} {self._unit_of_measurement[3:]}"
        }

    def update(self):
        """Update current values."""
        self._binance_data.update()
        for position in self._binance_data.positions:
            if position["symbol"] == self._symbol:
                self._state = position["positionAmt"]
                self._position_amount = position["positionAmt"]
                self._unrealized_profit = position["unrealizedProfit"]

        for ticker in self._binance_data.tickers:
            if ticker["symbol"] == self._symbol:
                self._native_balance = round(
                    float(ticker["price"]) * float(self._position_amount), 2
                )
                break

class BinanceExchangeSensor(SensorEntity):
    """Representation of a Sensor."""

    def __init__(self, binance_data, name, symbol, price):
        """Initialize the sensor."""
        self._binance_data = binance_data
        self._name = f"{name} {symbol} Exchange"
        self._symbol = symbol
        self._price = price
        self._unit_of_measurement = None
        self._state = None

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement this sensor expresses itself in."""
        return self._unit_of_measurement

    @property
    def icon(self):
        """Icon to use in the frontend, if any."""
        return CURRENCY_ICONS.get(self._unit_of_measurement, DEFAULT_COIN_ICON)

    @property
    def extra_state_attributes(self):
        """Return the state attributes of the sensor."""

        return {
            ATTR_ATTRIBUTION: ATTRIBUTION,
        }

    def update(self):
        """Update current values."""
        self._binance_data.update()
        for ticker in self._binance_data.tickers:
            if ticker["symbol"] == self._symbol:
                self._state = ticker["price"]
                if ticker["symbol"][-4:] in QUOTE_ASSETS[2:5]:
                    self._unit_of_measurement = ticker["symbol"][-4:]
                elif ticker["symbol"][-3:] in QUOTE_ASSETS[:2]:
                    self._unit_of_measurement = ticker["symbol"][-3:]
                break
