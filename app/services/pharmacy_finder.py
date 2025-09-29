"""Pharmacy finder service for locating nearby pharmacies with pricing information."""
from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Dict, List, Optional
import math


@dataclass(slots=True)
class Pharmacy:
    name: str
    address: str
    phone: str
    distance_miles: float
    latitude: float
    longitude: float
    services: List[str]
    pricing_tier: str  # "low", "medium", "high"
    accepts_insurance: bool = True


class PharmacyFinder:
    """Service for finding nearby pharmacies and their pricing information."""

    def __init__(self):
        # Mock pharmacy data - in a real implementation, this would come from APIs like:
        # - Google Places API
        # - Pharmacy benefit manager APIs
        # - GoodRx API
        # - Chain pharmacy APIs
        self._mock_pharmacies = [
            Pharmacy(
                name="Walmart Pharmacy",
                address="1500 N State St, Suite 100",
                phone="(555) 123-4567",
                distance_miles=0.3,
                latitude=40.7128,
                longitude=-74.0060,
                services=["Generic prescriptions", "Immunizations", "Health screenings", "$4 generic program"],
                pricing_tier="low",
                accepts_insurance=True
            ),
            Pharmacy(
                name="Costco Pharmacy",
                address="2200 Commerce Dr",
                phone="(555) 234-5678",
                distance_miles=0.8,
                latitude=40.7589,
                longitude=-73.9851,
                services=["Bulk prescriptions", "Immunizations", "Member pricing"],
                pricing_tier="low",
                accepts_insurance=True
            ),
            Pharmacy(
                name="CVS Pharmacy",
                address="850 Main Ave",
                phone="(555) 345-6789",
                distance_miles=0.4,
                latitude=40.7505,
                longitude=-73.9934,
                services=["24/7 location", "MinuteClinic", "Digital receipts", "ExtraCare rewards"],
                pricing_tier="medium",
                accepts_insurance=True
            ),
            Pharmacy(
                name="Walgreens",
                address="425 Oak Street",
                phone="(555) 456-7890",
                distance_miles=0.6,
                latitude=40.7614,
                longitude=-73.9776,
                services=["Drive-thru", "Vaccinations", "Health corner", "myWalgreens rewards"],
                pricing_tier="medium",
                accepts_insurance=True
            ),
            Pharmacy(
                name="Rite Aid",
                address="1200 Pine Street",
                phone="(555) 567-8901",
                distance_miles=1.2,
                latitude=40.7282,
                longitude=-73.9942,
                services=["wellness+ rewards", "Immunizations", "Health screenings"],
                pricing_tier="medium",
                accepts_insurance=True
            ),
            Pharmacy(
                name="Independent Family Pharmacy",
                address="678 Elm Avenue",
                phone="(555) 678-9012",
                distance_miles=1.5,
                latitude=40.7831,
                longitude=-73.9712,
                services=["Personalized service", "Compounding", "Free delivery", "Medication synchronization"],
                pricing_tier="high",
                accepts_insurance=True
            )
        ]

    def find_nearby_pharmacies(
        self, 
        location: str, 
        radius_miles: float = 5.0, 
        limit: int = 10,
        pricing_preference: Optional[str] = None
    ) -> List[Dict[str, object]]:
        """Find pharmacies near the given location.
        
        Args:
            location: ZIP code, city, or address
            radius_miles: Search radius in miles
            limit: Maximum number of results
            pricing_preference: Filter by pricing tier ("low", "medium", "high")
            
        Returns:
            List of pharmacy dictionaries with details and distance
        """
        # In a real implementation, you would:
        # 1. Geocode the location using Google Maps API or similar
        # 2. Query pharmacy databases or APIs
        # 3. Calculate actual distances
        
        pharmacies = self._mock_pharmacies.copy()
        
        # Filter by pricing preference if specified
        if pricing_preference and pricing_preference in ["low", "medium", "high"]:
            pharmacies = [p for p in pharmacies if p.pricing_tier == pricing_preference]
        
        # Filter by radius (using mock distances)
        pharmacies = [p for p in pharmacies if p.distance_miles <= radius_miles]
        
        # Sort by distance
        pharmacies.sort(key=lambda p: p.distance_miles)
        
        # Convert to dictionaries and limit results
        results = []
        for pharmacy in pharmacies[:limit]:
            results.append({
                "name": pharmacy.name,
                "address": pharmacy.address,
                "phone": pharmacy.phone,
                "distance_miles": pharmacy.distance_miles,
                "distance_display": f"{pharmacy.distance_miles:.1f} miles",
                "services": pharmacy.services,
                "pricing_tier": pharmacy.pricing_tier,
                "accepts_insurance": pharmacy.accepts_insurance,
                "estimated_savings": self._calculate_estimated_savings(pharmacy.pricing_tier)
            })
        
        return results
    
    def _calculate_estimated_savings(self, pricing_tier: str) -> str:
        """Calculate estimated savings message based on pricing tier."""
        savings_map = {
            "low": "Up to 80% savings on generics",
            "medium": "Up to 60% savings on generics", 
            "high": "Competitive generic pricing"
        }
        return savings_map.get(pricing_tier, "Competitive pricing")
    
    def get_pharmacy_details(self, pharmacy_name: str) -> Optional[Dict[str, object]]:
        """Get detailed information about a specific pharmacy."""
        for pharmacy in self._mock_pharmacies:
            if pharmacy.name.lower() == pharmacy_name.lower():
                return {
                    "name": pharmacy.name,
                    "address": pharmacy.address,
                    "phone": pharmacy.phone,
                    "services": pharmacy.services,
                    "pricing_tier": pharmacy.pricing_tier,
                    "accepts_insurance": pharmacy.accepts_insurance,
                    "estimated_savings": self._calculate_estimated_savings(pharmacy.pricing_tier),
                    "hours": self._get_mock_hours(pharmacy.name),
                    "website": self._get_mock_website(pharmacy.name)
                }
        return None
    
    def _get_mock_hours(self, pharmacy_name: str) -> str:
        """Return mock hours for pharmacy."""
        if "24/7" in pharmacy_name or "CVS" in pharmacy_name:
            return "24 hours"
        elif "Walmart" in pharmacy_name:
            return "Mon-Sun: 7AM-10PM"
        elif "Costco" in pharmacy_name:
            return "Mon-Fri: 10AM-8:30PM, Sat: 9:30AM-6PM, Sun: 10AM-6PM"
        else:
            return "Mon-Fri: 9AM-9PM, Sat: 9AM-7PM, Sun: 10AM-6PM"
    
    def _get_mock_website(self, pharmacy_name: str) -> str:
        """Return mock website for pharmacy."""
        if "CVS" in pharmacy_name:
            return "https://www.cvs.com/store-locator"
        elif "Walgreens" in pharmacy_name:
            return "https://www.walgreens.com/store-locator"
        elif "Walmart" in pharmacy_name:
            return "https://www.walmart.com/pharmacy"
        elif "Costco" in pharmacy_name:
            return "https://www.costco.com/pharmacy"
        elif "Rite Aid" in pharmacy_name:
            return "https://www.riteaid.com/pharmacy"
        else:
            return "https://example.com"