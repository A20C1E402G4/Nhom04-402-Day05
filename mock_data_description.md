# VSSA (VinFast Smart Sales Agent) Mock Data Architecture

To support the API-First Agentic Workflow without relying on a complex vector database, the mock data is structured into
explicit, LLM-friendly JSON files. This ensures 100% precision when the agent calls functions like `get_vehicle_data` or
`calculate_loan`.

Below is the description and example structure for each required dataset.

---

## 1. Vehicle Database (`vehicles.json`)

**Description:** Stores all specifications, pricing, and features for VinFast EV models. The agent queries this file to
answer questions about budget matching, vehicle range, and battery subscription costs.

**Example Data:**

```json
{
  "VF5": {
    "model_name": "VinFast VF 5 Plus",
    "versions": {
      "plus": {
        "price_without_battery_vnd": 468000000,
        "price_with_battery_vnd": 548000000,
        "battery_subscription_fee_per_month_vnd": 1600000,
        "max_range_km": 326.4,
        "seats": 5,
        "key_features": [
          "Nhỏ gọn đi phố",
          "Trợ lý ảo VinFast",
          "Cảnh báo điểm mù"
        ]
      }
    }
  },
  "VF7": {
    "model_name": "VinFast VF 7",
    "versions": {
      "base": {
        "price_without_battery_vnd": 850000000,
        "price_with_battery_vnd": 1050000000,
        "battery_subscription_fee_per_month_vnd": 2900000,
        "max_range_km": 375,
        "seats": 5,
        "key_features": [
          "Thiết kế thể thao",
          "Màn hình HUD"
        ]
      }
    }
  }
}
```

---

## 2. Finance & Promotions (`finance.json`)

**Description:** Contains banking partner details for loan calculations and current promotional campaigns. The agent
uses this to build accurate cash-flow tables (TCO) and apply discounts.

**Example Data:**

```json
{
  "banking_partners": {
    "vietcombank": {
      "bank_name": "Vietcombank",
      "interest_rate_percent_per_year": 8.5,
      "max_loan_percentage": 80,
      "max_duration_months": 96
    },
    "techcombank": {
      "bank_name": "Techcombank",
      "interest_rate_percent_per_year": 9.0,
      "max_loan_percentage": 85,
      "max_duration_months": 84
    }
  },
  "current_promotions": [
    {
      "promo_code": "VF7_FREE_CHARGE_1YR",
      "applicable_models": [
        "VF7",
        "VF8"
      ],
      "discount_amount_vnd": 0,
      "description": "Miễn phí sạc pin tại trạm công cộng trong 1 năm"
    }
  ]
}
```

---

## 3. Showrooms & Booking Data (`showrooms.json`)

**Description:** Defines physical showroom locations, coordinates, available test drive models, and booking slots. Used
when the agent attempts to "chốt lịch lái thử" (close a test drive).

**Example Data:**

```json
{
  "SR_Q9": {
    "showroom_name": "VinFast Thảo Điền",
    "address": "Vincom Mega Mall Thảo Điền, TP Thủ Đức",
    "coordinates": {
      "lat": 10.8023,
      "lng": 106.7402
    },
    "available_test_drive_models": [
      "VF5",
      "VF6",
      "VF7"
    ],
    "available_time_slots": [
      "2026-04-10T09:00:00",
      "2026-04-10T14:30:00"
    ]
  },
  "SR_Q1": {
    "showroom_name": "VinFast Đồng Khởi",
    "address": "Vincom Center Đồng Khởi, Quận 1",
    "coordinates": {
      "lat": 10.7779,
      "lng": 106.7020
    },
    "available_test_drive_models": [
      "VF8",
      "VF9"
    ],
    "available_time_slots": [
      "2026-04-10T11:00:00",
      "2026-04-12T15:00:00"
    ]
  }
}
```

---

## 4. Energy & Charging Station Database (`charging_stations.json`)

**Description:** Provides the constants needed to calculate the Total Cost of Ownership (TCO). Instead of hardcoding
routes, charging stations are stored as independent geographical entities. When the agent calls
`find_charging_stations(origin, destination)`, the underlying Python tool will mock a Maps API integration by filtering
these stations based on their coordinates (e.g., using a bounding box or distance calculation between District 9 and
Vung Tau).

**Example Data:**

```json
{
  "tco_constants": {
    "current_electricity_price_vnd_per_kwh": 3858,
    "average_gas_price_vnd_per_liter": 24000,
    "co2_emission_reduction_kg_per_km": 0.15
  },
  "charging_stations": {
    "ST_VT01": {
      "location_name": "Trạm dừng chân cao tốc Long Thành",
      "address": "Cao tốc TPHCM - Long Thành - Dầu Giây",
      "coordinates": {
        "lat": 10.7412,
        "lng": 107.0112
      },
      "charger_types": [
        "DC 60kW",
        "DC 250kW"
      ],
      "status": "operational"
    },
    "ST_VT02": {
      "location_name": "Vincom Plaza Vũng Tàu",
      "address": "Phường 7, TP Vũng Tàu",
      "coordinates": {
        "lat": 10.3541,
        "lng": 107.0858
      },
      "charger_types": [
        "AC 11kW",
        "DC 60kW"
      ],
      "status": "operational"
    },
    "ST_HCM01": {
      "location_name": "Khu công nghệ cao Quận 9",
      "address": "Phường Tân Phú, TP Thủ Đức (Quận 9)",
      "coordinates": {
        "lat": 10.8461,
        "lng": 106.7930
      },
      "charger_types": [
        "AC 11kW",
        "DC 250kW"
      ],
      "status": "operational"
    },
    "ST_HCM02": {
      "location_name": "Vincom Center Đồng Khởi",
      "address": "72 Lê Thánh Tôn, Quận 1",
      "coordinates": {
        "lat": 10.7779,
        "lng": 106.7020
      },
      "charger_types": [
        "AC 11kW"
      ],
      "status": "operational"
    }
  }
}
```

When you write the logic for `find_charging_stations(origin, destination)` in your `tools.py`, you can now program it to
behave like a real routing engine:

1. **Mock the Map API:** The function can take the origin ("Quận 9") and destination ("Quận 1" or "Vũng Tàu").
2. **Filter geographically:** It iterates through the `charging_stations` dictionary and selects stations that logically
   fall along that path (you can just use a simple mock logic in Python that returns `ST_HCM01` and `ST_HCM02` for the
   city route, or `ST_VT01` and `ST_VT02` for the Vung Tau route).
3. **Return data to the LLM:** The LLM receives the dynamically filtered list and uses it to reassure the customer ("*Có
   2 trạm sạc siêu nhanh trên đường bạn về Vũng Tàu...*").

---

## 5. Evaluation Test Cases (`test_cases.json`)

**Description:** A suite of predefined user prompts mapped directly from the "4 Paths" in the product spec. This file is
ingested by `tests/test_agent_graph.py` to assert the agent triggers the correct intent, calls the required tools, and
hits the 100% precision target.

**Example Data:**

```json
[
  {
    "test_id": "TC_01_HAPPY_PATH",
    "user_query": "Tôi có 800 triệu, nhà 4 người, ở chung cư, nên mua xe nào?",
    "expected_intent": "vehicle_consulting",
    "expected_tool_calls": [
      "get_vehicle_data",
      "calculate_loan"
    ]
  },
  {
    "test_id": "TC_02_GREEN_ROUTE",
    "user_query": "Tôi đi làm từ Quận 9 sang Quận 1 mỗi ngày, cuối tuần hay về quê ở Vũng Tàu thì có trạm sạc không?",
    "expected_intent": "route_planning",
    "expected_tool_calls": [
      "find_charging_stations"
    ]
  },
  {
    "test_id": "TC_03_LOW_CONFIDENCE",
    "user_query": "Xe VF 8 ghế lái có bọc da Nappa giống xe Đức không?",
    "expected_intent": "out_of_knowledge_base",
    "expected_behavior": "graceful_degradation_fallback"
  }
]
```
