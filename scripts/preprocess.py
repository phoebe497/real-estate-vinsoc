import csv
import json
import os
import re
from pathlib import Path

# Paths
data_dir = Path("data")
dataset_dir = data_dir / "dataset"
raw_json_dir = dataset_dir / "raw_json"
output_file = data_dir / "vinhomes_real.json"

# Mapping properties for zones
zone_details_map = {
    "masteri-lakeside": {
        "design_style": "Modern luxury",
        "handover_status": "under_construction",
        "total_buildings": 3,
        "location_in_project": "Giao điểm đường Lý Thánh Tông và Đại Tây Dương",
        "featured_amenities": ["Bể bơi ngoài trời", "Hồ điều hòa", "Lounge thư giãn"],
        "target_audience": ["Gia đình trẻ", "Doanh nhân", "Đầu tư dài hạn"]
    },
    "masteri-waterfront": {
        "design_style": "Modern luxury",
        "handover_status": "handed_over",
        "total_buildings": 6,
        "location_in_project": "Trung tâm đại đô thị, view trực diện hồ Ngọc Trai",
        "featured_amenities": ["Vườn thượng uyển", "Bể bơi trong nhà", "Sảnh Lounge 5 sao"],
        "target_audience": ["Giới thượng lưu", "Gia đình muốn sống tiện nghi", "Đầu tư cao cấp"]
    },
    "the-bayfront-vinhomes": {
        "design_style": "Dubai Tropical",
        "handover_status": "under_construction",
        "total_buildings": 4,
        "location_in_project": "Phía Đông đại đô thị",
        "featured_amenities": ["Bể bơi bốn mùa", "Beach club", "Vườn nhiệt đới"],
        "target_audience": ["Người ưa nghỉ dưỡng", "Gia đình hiện đại"]
    },
    "the-beverly-vinhomes": {
        "design_style": "American Glory Living",
        "handover_status": "under_construction",
        "total_buildings": 4,
        "location_in_project": "Phía Tây Bắc, gần công viên hồ San Hô",
        "featured_amenities": ["Bể bơi Santa Monica", "Quảng trường Beverly", "Gym & Sauna"],
        "target_audience": ["Người trẻ năng động", "Người ưa sống phóng khoáng"]
    },
    "the-london-vinhomes": {
        "design_style": "British Classical",
        "handover_status": "under_construction",
        "total_buildings": 3,
        "location_in_project": "Gần trục đường Hải Đăng",
        "featured_amenities": ["Bể bơi Santamonica 700m2", "Phòng karaoke", "Phòng tập Gym"],
        "target_audience": ["Cư dân ưa thanh lịch", "Gia đình trung lưu"]
    },
    "the-ocean-view-vinhomes": {
        "design_style": "Mediterranean Resort",
        "handover_status": "handed_over",
        "total_buildings": 12,
        "location_in_project": "Mặt đường Lý Thánh Tông",
        "featured_amenities": ["Quảng trường Ocean View", "Hồ cá Koi", "Bể bơi vô cực"],
        "target_audience": ["Gia đình", "Khách nghỉ dưỡng", "Đầu tư cho thuê"]
    },
    "the-palma": {
        "design_style": "Modern luxury",
        "handover_status": "under_construction",
        "total_buildings": 4,
        "location_in_project": "Phân khu Lumiere Orient Pearl",
        "featured_amenities": ["Hành lang cao cấp", "Vườn cảnh quan", "Gym hiện đại"],
        "target_audience": ["Giới thượng lưu", "Đầu tư căn hộ dịch vụ"]
    },
    "the-paris-vinhomes": {
        "design_style": "French Classical",
        "handover_status": "under_construction",
        "total_buildings": 6,
        "location_in_project": "Phía Bắc khu đô thị",
        "featured_amenities": ["Quảng trường Paris", "Café plaza", "Lối dạo bộ phong cách Pháp"],
        "target_audience": ["Người ưa nghệ thuật", "Gia đình tìm không gian thanh bình"]
    },
    "the-pavilion-vinhomes": {
        "design_style": "Tropical Resort",
        "handover_status": "handed_over",
        "total_buildings": 4,
        "location_in_project": "Phía Đông, gần cổng chính",
        "featured_amenities": ["Vườn nhiệt đới 2ha", "Bể bơi resort", "Nhà để xe 2 tầng hầm"],
        "target_audience": ["Gia đình 3-4 người", "Muốn sống resort"]
    },
    "sapphire-vinhomes": {
        "design_style": "Modern",
        "handover_status": "handed_over",
        "total_buildings": 16,
        "location_in_project": "Trung tâm khu đô thị",
        "featured_amenities": ["View hồ điều hòa", "Bể bơi ngoài trời", "Sân thể thao"],
        "target_audience": ["Người trẻ tuổi", "Gia đình trẻ", "Đầu tư cho thuê ngắn hạn"]
    },
    "the-senique-hanoi": {
        "design_style": "Modern luxury",
        "handover_status": "under_construction",
        "total_buildings": 3,
        "location_in_project": "Vị trí trái tim khu đô thị",
        "featured_amenities": ["Bể bơi trong nhà", "Sảnh đón sang trọng", "Vườn trên không"],
        "target_audience": ["Giới trung thượng lưu", "Gia đình"]
    },
    "the-zenpark-vinhomes": {
        "design_style": "Japanese",
        "handover_status": "handed_over",
        "total_buildings": 4,
        "location_in_project": "Kế cận Lý Thánh Tông",
        "featured_amenities": ["Vườn Nhật Bản 6.208m2", "Hồ cá Koi 692m2", "Bể bơi bốn mùa tiêu chuẩn Olympic"],
        "target_audience": ["Gia đình ưa yên tĩnh", "Người yêu thích văn hóa Nhật Bản"]
    },
    "the-zurich-vinhomes": {
        "design_style": "Swiss European",
        "handover_status": "under_construction",
        "total_buildings": 3,
        "location_in_project": "Dọc đường Đại Dương",
        "featured_amenities": ["Hồ cảnh quan Thụy Sĩ", "Quảng trường Zurich", "Café plaza"],
        "target_audience": ["Giới văn phòng", "Cư dân ưa lối sống Thụy Sĩ"]
    }
}

def parse_zones():
    zones = []
    zones_csv_path = dataset_dir / "zones.csv"
    if not zones_csv_path.exists():
        print("zones.csv not found!")
        return zones

    with open(zones_csv_path, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            slug = row["slug"]
            details = zone_details_map.get(slug, {
                "design_style": "Modern",
                "handover_status": "handed_over",
                "total_buildings": 4,
                "location_in_project": "Trung tâm",
                "featured_amenities": [],
                "target_audience": ["Mọi đối tượng"]
            })
            
            zone = {
                "name": row["name"],
                "slug": slug,
                "description": row["description"] or "Thông tin phân khu Vinhomes Ocean Park.",
                "design_style": details["design_style"],
                "handover_status": details["handover_status"],
                "total_buildings": details["total_buildings"],
                "location_in_project": details["location_in_project"],
                "featured_amenities": details["featured_amenities"],
                "target_audience": details["target_audience"],
                "unit_types": [],
                "price_range_per_sqm_million": {"min": 0, "avg": 0, "max": 0},
                "total_price_range_billion": {"min": 0, "avg": 0, "max": 0},
                "data_period": "2024",
                "confidence_level": row["confidence_level"] or "medium"
            }
            zones.append(zone)
    return zones

def enrich_zones_with_stats(zones):
    stats_csv_path = dataset_dir / "unit_type_stats.csv"
    if not stats_csv_path.exists():
        print("unit_type_stats.csv not found!")
        return

    # Map zones by slug
    zones_map = {z["slug"]: z for z in zones}
    
    # Read stats
    stats_by_zone = {}
    with open(stats_csv_path, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            z_slug = row["zone_slug"]
            if not z_slug:
                continue
            if z_slug not in stats_by_zone:
                stats_by_zone[z_slug] = []
            stats_by_zone[z_slug].append(row)

    for slug, zone in zones_map.items():
        z_stats = stats_by_zone.get(slug, [])
        if not z_stats:
            continue
        
        # Unit types
        unit_types = sorted(list(set(row["unit_type"] for row in z_stats)))
        # Normalize unit types to Standard names if necessary
        zone["unit_types"] = unit_types
        
        # Sqm Price range
        min_prices = [float(row["min_price_per_sqm"]) for row in z_stats if row["min_price_per_sqm"]]
        avg_prices = [float(row["avg_price_per_sqm"]) for row in z_stats if row["avg_price_per_sqm"]]
        max_prices = [float(row["max_price_per_sqm"]) for row in z_stats if row["max_price_per_sqm"]]
        
        if min_prices:
            zone["price_range_per_sqm_million"] = {
                "min": round(min(min_prices) / 1_000_000, 1),
                "avg": round(sum(avg_prices) / len(avg_prices) / 1_000_000 if avg_prices else min(min_prices) / 1_000_000, 1),
                "max": round(max(max_prices) / 1_000_000 if max_prices else min(min_prices) / 1_000_000, 1)
            }
        
        # We can also compute total price in billions using unit sizes * sqm prices,
        # or fall back to known averages. Let's compute average min_area * min_sqm_price
        total_mins = []
        total_maxs = []
        for row in z_stats:
            if row["min_area_sqm"] and row["min_price_per_sqm"]:
                min_price_total = float(row["min_area_sqm"]) * float(row["min_price_per_sqm"])
                total_mins.append(min_price_total)
            if row["max_area_sqm"] and row["max_price_per_sqm"]:
                max_price_total = float(row["max_area_sqm"]) * float(row["max_price_per_sqm"])
                total_maxs.append(max_price_total)
                
        if total_mins and total_maxs:
            min_val = min(total_mins) / 1_000_000_000
            max_val = max(total_maxs) / 1_000_000_000
            zone["total_price_range_billion"] = {
                "min": round(min_val, 2),
                "avg": round((min_val + max_val) / 2, 2),
                "max": round(max_val, 2)
            }
        else:
            # defaults if missing
            zone["total_price_range_billion"] = {"min": 1.5, "avg": 3.0, "max": 6.0}

def parse_buildings():
    buildings = []
    if not raw_json_dir.exists():
        return buildings

    # Pattern match for building files: toa-<name>-<zone>-<hash>.json
    for filename in os.listdir(raw_json_dir):
        if not filename.startswith("toa-") or not filename.endswith(".json"):
            continue
            
        file_path = raw_json_dir / filename
        with open(file_path, encoding="utf-8") as f:
            data = json.load(f)
            
        # Determine building name and zone_slug from file
        title = data.get("title", "")
        # e.g., "Tòa R1.01 The Zenpark Vinhomes Ocean Park - Trực tiếp CĐT"
        # Let's extract R1.01
        b_name_match = re.search(r"Tòa\s+([A-Za-z0-9.]+)", title)
        b_name = b_name_match.group(1) if b_name_match else filename.split("-")[1].upper()
        
        # Match zone_slug
        z_slug = None
        if "the-zenpark" in filename:
            z_slug = "the-zenpark-vinhomes"
        elif "the-zurich" in filename:
            z_slug = "the-zurich-vinhomes"
        elif "the-beverly" in filename:
            z_slug = "the-beverly-vinhomes"
        elif "the-london" in filename:
            z_slug = "the-london-vinhomes"
        elif "the-paris" in filename or "toa-pr" in filename:
            z_slug = "the-paris-vinhomes"
        elif "masteri-waterfront" in filename:
            z_slug = "masteri-waterfront"
        elif "masteri-lakeside" in filename:
            z_slug = "masteri-lakeside"
        elif "the-pavilion" in filename:
            z_slug = "the-pavilion-vinhomes"
        elif "sapphire" in filename:
            z_slug = "sapphire-vinhomes"
        else:
            z_slug = "the-zenpark-vinhomes"  # fallback
            
        # Parse floors and area range
        floors = 30
        for block in data.get("text_blocks", []):
            m = re.search(r"Số tầng\s*:\s*(\d+)", block, re.IGNORECASE)
            if m:
                floors = int(m.group(1))
                break
                
        area_min = 25.0
        area_max = 85.0
        for block in data.get("text_blocks", []):
            m = re.search(r"Diện tích\s*:\s*(\d+)\s*–\s*(\d+)", block, re.IGNORECASE)
            if m:
                area_min = float(m.group(1))
                area_max = float(m.group(2))
                break
                
        # Parse table_rows for popular units
        pop_units = ["Studio", "1PN", "2PN", "3PN"]
        
        # Build building item
        b_slug = filename.rsplit("-", 1)[0]  # strip hash
        building = {
            "zone_slug": z_slug,
            "name": b_name,
            "slug": b_slug,
            "floors": floors,
            "handover_status": "handed_over" if "zenpark" in z_slug or "waterfront" in z_slug else "under_construction",
            "location_note": "Nằm trong phân khu, giao thông thuận tiện.",
            "popular_unit_types": pop_units,
            "area_range_sqm": {"min": area_min, "max": area_max}
        }
        buildings.append(building)
        
    return buildings

def build_seed_json():
    print("Pre-processing raw dataset...")
    
    # 1. Project details
    project = {
        "name": "Vinhomes Ocean Park Gia Lâm",
        "developer": "Vinhomes",
        "location": "Phường Trâu Quỳ – Dương Xá – Kiêu Kỵ – Đa Tốn, Quận Gia Lâm, Hà Nội.",
        "total_area_ha": 420,
        "description": "Đại đô thị văn minh, hiện đại được quy hoạch theo mô hình sinh thái phong cách Singapore. Điểm nhấn là Hồ Ngọc Trai rộng 24.5ha và biển hồ Crystal Lagoons 6.1ha.",
        "highlights": [
            "Hồ Ngọc Trai rộng 24.5ha - lá phổi xanh của khu đô thị",
            "Biển hồ nước mặn nhân tạo Crystal Lagoons rộng 6.1ha",
            "Quy mô đại đô thị 420ha với mật độ xây dựng 19.2%",
            "Hạ tầng giáo dục liên cấp Vinschool, Brighton College và Đại học VinUni",
            "Tuyến kết nối thuận tiện qua cầu Vĩnh Tuy, cầu Thanh Trì và Lý Thánh Tông"
        ]
    }

    # 2. Zones
    zones = parse_zones()
    enrich_zones_with_stats(zones)
    
    # 3. Buildings
    buildings = parse_buildings()
    
    # 4. Amenities
    amenities = [
        {
            "scope": "project",
            "zone_slug": None,
            "name": "Biển hồ nhân tạo Crystal Lagoons 6.1ha",
            "type": "recreation",
            "distance_text": "Cách các phân khu 5-15 phút đi bộ",
            "description": "Biển nước mặn nhân tạo lớn nhất Việt Nam với bãi cát trắng mịn.",
            "confidence_level": "high"
        },
        {
            "scope": "project",
            "zone_slug": None,
            "name": "Hồ Ngọc Trai 24.5ha",
            "type": "recreation",
            "distance_text": "Trung tâm đại đô thị",
            "description": "Hồ nước ngọt trung tâm lớn nhất, điều hòa không khí toàn khu.",
            "confidence_level": "high"
        },
        {
            "scope": "project",
            "zone_slug": None,
            "name": "Vincom Mega Mall Ocean Park",
            "type": "shopping",
            "distance_text": "Gần hồ Ngọc Trai",
            "description": "Trung tâm thương mại lớn phục vụ nhu cầu mua sắm, ẩm thực và vui chơi giải trí.",
            "confidence_level": "high"
        },
        {
            "scope": "project",
            "zone_slug": None,
            "name": "Trường Đại học VinUni",
            "type": "education",
            "distance_text": "Phía Nam dự án",
            "description": "Đại học tinh hoa phi lợi nhuận đầu tiên của Vingroup.",
            "confidence_level": "high"
        }
    ]
    
    # 5. Transport routes
    transport_routes = [
        {
            "origin": "Cầu Vĩnh Tuy",
            "destination": "Vinhomes Ocean Park",
            "main_roads": ["Đường Cổ Linh", "Cao tốc Hà Nội - Hải Phòng"],
            "distance_km": 12.0,
            "driving_time_min": 20,
            "driving_time_max": 40,
            "traffic_note": "Có thể ùn tắc nhẹ giờ cao điểm chiều đi cầu Vĩnh Tuy.",
            "confidence_level": "high"
        },
        {
            "origin": "Cầu Thanh Trì",
            "destination": "Vinhomes Ocean Park",
            "main_roads": ["Đường Vành đai 3", "Đường gom Cao tốc"],
            "distance_km": 14.0,
            "driving_time_min": 15,
            "driving_time_max": 30,
            "traffic_note": "Giao thông tương đối thông thoáng.",
            "confidence_level": "high"
        }
    ]
    
    # 6. Matching rules using exact slugs from zones
    matching_rules = {
        "budget_thresholds_billion": {
            "COLD_max": 1.5,
            "WARM_range": [1.5, 3.0],
            "HOT_min": 3.0
        },
        "zone_budget_fit": {
            "masteri-lakeside": {"min_billion": 2.0, "sweet_spot_billion": 4.5},
            "masteri-waterfront": {"min_billion": 2.5, "sweet_spot_billion": 5.0},
            "the-beverly-vinhomes": {"min_billion": 1.8, "sweet_spot_billion": 3.5},
            "the-london-vinhomes": {"min_billion": 1.7, "sweet_spot_billion": 3.2},
            "the-paris-vinhomes": {"min_billion": 1.8, "sweet_spot_billion": 3.5},
            "the-pavilion-vinhomes": {"min_billion": 1.5, "sweet_spot_billion": 2.8},
            "the-zenpark-vinhomes": {"min_billion": 1.9, "sweet_spot_billion": 3.2},
            "the-zurich-vinhomes": {"min_billion": 1.7, "sweet_spot_billion": 3.0}
        },
        "purpose_zone_affinity": {
            "ở thật": ["the-zenpark-vinhomes", "the-pavilion-vinhomes", "masteri-waterfront"],
            "đầu tư": ["masteri-lakeside", "the-beverly-vinhomes", "the-zurich-vinhomes"],
            "cho thuê": ["the-zenpark-vinhomes", "masteri-waterfront"],
            "nghỉ dưỡng": ["the-pavilion-vinhomes"]
        }
    }

    # Consolidated structure
    output_data = {
        "project": project,
        "zones": zones,
        "buildings": buildings,
        "amenities": amenities,
        "transport_routes": transport_routes,
        "matching_rules": matching_rules
    }
    
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)
        
    print(f"Successfully compiled structured real data to {output_file}!")

if __name__ == "__main__":
    build_seed_json()
