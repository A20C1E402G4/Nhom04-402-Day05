import json
import os
import math

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")

def load_json(filename):
    path = os.path.join(DATA_DIR, filename)
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def get_vehicle_data(model_id: str):
    """
    Truy vấn thông số kỹ thuật và giá của một dòng xe VinFast.
    model_id: hID của xe (VD: VF3, VF5, VF7, VF8, VF9)
    """
    vehicles = load_json("vehicles.json")
    return vehicles.get(model_id.upper(), {"error": "Không tìm thấy thông tin xe."})

def calculate_loan_plan(model_id: str, version: str, loan_percentage: float, duration_months: int, bank_id: str = "vietcombank"):
    """
    Tính toán phương án tài chính trả góp cho một dòng xe.
    """
    vehicles = load_json("vehicles.json")
    finance = load_json("finance.json")
    
    car = vehicles.get(model_id.upper())
    if not car:
        return {"error": "Không tìm thấy xe."}
    
    version_data = car["versions"].get(version.lower())
    if not version_data:
        return {"error": f"Không tìm thấy phiên bản {version} cho xe {model_id}."}
    
    bank = finance["banking_partners"].get(bank_id.lower())
    if not bank:
        return {"error": "Không tìm thấy thông tin ngân hàng."}

    price = version_data["price_with_battery_vnd"]
    loan_amount = price * (loan_percentage / 100)
    prepaid_amount = price - loan_amount
    
    # Tính lãi suất hàng tháng
    annual_rate = bank["interest_rate_percent_per_year"] / 100
    monthly_rate = annual_rate / 12
    
    # Công thức dư nợ giảm dần (amortization)
    if monthly_rate > 0:
        monthly_payment = (loan_amount * monthly_rate * pow(1 + monthly_rate, duration_months)) / (pow(1 + monthly_rate, duration_months) - 1)
    else:
        monthly_payment = loan_amount / duration_months

    return {
        "model_name": car["model_name"],
        "version": version.upper(),
        "total_price": price,
        "loan_amount": int(loan_amount),
        "prepaid_amount": int(prepaid_amount),
        "interest_rate": f"{bank['interest_rate_percent_per_year']}%",
        "duration_months": duration_months,
        "estimated_monthly_payment": int(monthly_payment)
    }

def calculate_tco_comparison(model_id: str, version: str, monthly_km: float = 1500):
    """
    So sánh tổng chi phí sở hữu (TCO) giữa xe điện VinFast và xe xăng tương đương trong 1 năm.
    """
    vehicles = load_json("vehicles.json")
    stations_data = load_json("charging_stations.json")
    constants = stations_data["tco_constants"]
    
    car = vehicles.get(model_id.upper())
    if not car:
        return {"error": "Không tìm thấy xe."}
    
    version_data = car["versions"].get(version.lower())
    if not version_data:
        return {"error": "Không tìm thấy phiên bản."}

    # Giả định mức tiêu thụ năng lượng
    # Xe điện: ~0.15 kWh/km (trung bình cho SUV)
    # Xe xăng tương đương: ~0.09 L/km (9 lít / 100km)
    ev_consumption_kwh_per_km = 0.15 
    gas_consumption_l_per_km = 0.09 

    # Chi phí điện (thuê pin + sạc)
    monthly_electricity_cost = (monthly_km * ev_consumption_kwh_per_km) * constants["current_electricity_price_vnd_per_kwh"]
    monthly_battery_fee = version_data["battery_subscription_fee_per_month_vnd"]
    total_ev_monthly = monthly_electricity_cost + monthly_battery_fee

    # Chi phí xăng
    total_gas_monthly = (monthly_km * gas_consumption_l_per_km) * constants["average_gas_price_vnd_per_liter"]

    # Tiết kiệm
    monthly_saving = total_gas_monthly - total_ev_monthly
    yearly_saving = monthly_saving * 12
    co2_reduction = (monthly_km * constants["co2_emission_reduction_kg_per_km"]) * 12

    return {
        "model_name": car["model_name"],
        "monthly_km": monthly_km,
        "ev_cost_per_month": int(total_ev_monthly),
        "gas_cost_per_month": int(total_gas_monthly),
        "monthly_saving": int(monthly_saving),
        "yearly_saving": int(yearly_saving),
        "co2_reduction_kg_per_year": round(co2_reduction, 1)
    }

def book_test_drive(name: str, phone: str, model_id: str, showroom_id: str, time_slot: str):
    """
    Đặt lịch lái thử xe tại showroom.
    """
    showrooms = load_json("showrooms.json")
    sr = showrooms.get(showroom_id.upper())
    if not sr:
        return {"error": "Không tìm thấy Showroom."}
    
    # Mock lưu vào file
    booking_data = {
        "customer_name": name,
        "phone": phone,
        "model": model_id.upper(),
        "showroom": sr["showroom_name"],
        "time": time_slot,
        "status": "confirmed"
    }
    
    # Ghi log booking (giả lập database)
    path = os.path.join(DATA_DIR, "bookings.json")
    bookings = []
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                bookings = json.load(f)
        except:
            bookings = []
    
    bookings.append(booking_data)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(bookings, f, indent=2, ensure_ascii=False)
        
    return {
        "status": "success",
        "message": f"Chúc mừng {name}, lịch lái thử xe {model_id} tại {sr['showroom_name']} vào lúc {time_slot} đã được xác nhận!",
        "booking_details": booking_data
    }

def find_charging_stations(origin: str, destination: str):
    """
    Tìm kiếm trạm sạc trên lộ trình của khách hàng.
    Mock logic based on keywords in origin/destination.
    """
    data = load_json("charging_stations.json")
    all_stations = data["charging_stations"]
    
    # Mock routing logic
    route_keywords = {
        "vũng tàu": ["ST_VT01", "ST_VT02"],
        "quận 9": ["ST_HCM01"],
        "quận 1": ["ST_HCM02"],
        "thảo điền": ["ST_HCM02"]
    }
    
    target_stations = []
    text = (origin + " " + destination).lower()
    
    for kw, ids in route_keywords.items():
        if kw in text:
            for s_id in ids:
                if s_id in all_stations and all_stations[s_id] not in target_stations:
                    target_stations.append(all_stations[s_id])
    
    if not target_stations:
        # Fallback: return any operational station nearby
        return {"message": "Không tìm thấy trạm sạc chính xác trên cung đường này, đây là các trạm lân cận.", "stations": list(all_stations.values())[:2]}

    return {"route": f"{origin} -> {destination}", "stations": target_stations}

if __name__ == "__main__":
    # Test
    print("Test Get Vehicle:")
    print(get_vehicle_data("VF7"))
    print("\nTest Loan Calculation:")
    print(calculate_loan_plan("VF7", "plus", 80, 60))
    print("\nTest Find Charging Stations:")
    print(find_charging_stations("Quận 9", "Vũng Tàu"))
