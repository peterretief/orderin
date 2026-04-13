"""
Distance calculation utilities for delivery costing.
Calculates distance between two addresses or coordinates.
"""

from decimal import Decimal
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
import logging

logger = logging.getLogger(__name__)


class DistanceCalculator:
    """Calculate distance between two locations."""
    
    def __init__(self):
        """Initialize the geocoder."""
        self.geocoder = Nominatim(user_agent="orderin_delivery")
    
    def geocode_address(self, address):
        """
        Convert an address to latitude/longitude coordinates.
        
        Args:
            address (str): Address string (e.g., "Cape Town Market, Epping, Cape Town")
        
        Returns:
            tuple: (latitude, longitude) or None if not found
        """
        try:
            location = self.geocoder.geocode(address)
            if location:
                return (Decimal(str(location.latitude)), Decimal(str(location.longitude)))
            else:
                logger.warning(f"Could not geocode address: {address}")
                return None
        except Exception as e:
            logger.error(f"Geocoding error for {address}: {e}")
            return None
    
    def calculate_distance_km(self, address1, address2):
        """
        Calculate distance between two addresses in kilometers.
        
        Args:
            address1 (str): First address
            address2 (str): Second address
        
        Returns:
            Decimal: Distance in kilometers, or None if calculation fails
        """
        try:
            # Geocode both addresses
            coords1 = self.geocode_address(address1)
            coords2 = self.geocode_address(address2)
            
            if not coords1 or not coords2:
                logger.warning(f"Could not geocode one or both addresses")
                return None
            
            # Calculate distance using geodesic (great-circle distance)
            distance_km = geodesic(
                (float(coords1[0]), float(coords1[1])),
                (float(coords2[0]), float(coords2[1]))
            ).kilometers
            
            return Decimal(str(round(distance_km, 2)))
        
        except Exception as e:
            logger.error(f"Distance calculation error: {e}")
            return None
    
    def calculate_distance_from_coords(self, lat1, lon1, lat2, lon2):
        """
        Calculate distance between two coordinates in kilometers.
        
        Args:
            lat1, lon1 (float/Decimal): First location coordinates
            lat2, lon2 (float/Decimal): Second location coordinates
        
        Returns:
            Decimal: Distance in kilometers
        """
        try:
            distance_km = geodesic(
                (float(lat1), float(lon1)),
                (float(lat2), float(lon2))
            ).kilometers
            
            return Decimal(str(round(distance_km, 2)))
        except Exception as e:
            logger.error(f"Coordinate distance calculation error: {e}")
            return None


class DeliveryDistanceAndCost:
    """Calculate both distance and delivery cost for an order."""
    
    def __init__(self, store_address, delivery_address):
        """
        Initialize with store and delivery addresses.
        
        Args:
            store_address (str): Store/warehouse address
            delivery_address (str): Customer delivery address
        """
        self.store_address = store_address
        self.delivery_address = delivery_address
        self.distance_calculator = DistanceCalculator()
        self.distance_km = None
    
    def geocode_address(self, address):
        """
        Geocode an address to coordinates.
        
        Args:
            address (str): Address to geocode
        
        Returns:
            tuple: (latitude, longitude) as Decimals, or None if not found
        """
        return self.distance_calculator.geocode_address(address)
    
    def calculate_distance(self):
        """Calculate distance between store and delivery address."""
        self.distance_km = self.distance_calculator.calculate_distance_km(
            self.store_address,
            self.delivery_address
        )
        return self.distance_km
    
    def get_delivery_cost(self, order_delivery):
        """
        Calculate delivery cost based on calculated distance.
        
        Args:
            order_delivery: OrderDelivery instance
        
        Returns:
            DeliveryCost instance with calculated costs
        """
        if not self.distance_km:
            self.calculate_distance()
        
        if not self.distance_km:
            # Fallback: use default minimum distance if calculation fails
            self.distance_km = Decimal('5')
        
        from .costing import DeliveryCostCalculator
        
        calculator = DeliveryCostCalculator(
            order_delivery=order_delivery,
            distance_km=self.distance_km,
            actual_weight_kg=self._calculate_order_weight(order_delivery)
        )
        
        return calculator.save_cost()
    
    def _calculate_order_weight(self, order_delivery):
        """Calculate total weight of order items."""
        from decimal import Decimal
        total_weight = Decimal('0')
        
        for item in order_delivery.order.items.all():
            if hasattr(item.product, 'weight_kg') and item.product.weight_kg:
                total_weight += Decimal(str(item.product.weight_kg)) * item.quantity
        
        return total_weight if total_weight > 0 else Decimal('0')


def calculate_delivery_distance_and_cost(
    store_address,
    delivery_address,
    order_delivery,
    actual_weight_kg=None,
    tax_percentage=15
):
    """
    Convenience function to calculate both distance and delivery cost.
    
    Args:
        store_address (str): Store/warehouse address
        delivery_address (str): Customer delivery address
        order_delivery: OrderDelivery instance
        actual_weight_kg (Decimal, optional): Override weight calculation
        tax_percentage (int): Tax rate percentage
    
    Returns:
        tuple: (distance_km, DeliveryCost instance)
    """
    calc = DeliveryDistanceAndCost(store_address, delivery_address)
    distance = calc.calculate_distance()
    
    # Override weight if provided
    if actual_weight_kg:
        from .costing import DeliveryCostCalculator
        calculator = DeliveryCostCalculator(order_delivery, distance, actual_weight_kg)
        cost = calculator.save_cost(tax_percentage)
    else:
        cost = calc.get_delivery_cost(order_delivery)
    
    return distance, cost


# Example usage:
# from delivery.distance import calculate_delivery_distance_and_cost
# 
# distance, cost = calculate_delivery_distance_and_cost(
#     store_address="Cape Town Market, Epping, Cape Town",
#     delivery_address="Observatory, Cape Town",
#     order_delivery=order_delivery
# )
# print(f"Distance: {distance}km")
# print(f"Delivery cost: R{cost.total_cost}")
