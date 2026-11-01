extends RefCounted
## Review-only Level 1 stat-rank acceptance.
## Does not modify combat, authorize character abilities, or set final balance.
## The current draft native battle adapter uses max_hp/max_mp; MAG is proposed
## presentation data until a creator-approved damage/healing formula binds it.

const IDS := ["ender", "lyra", "ionia", "reson", "aepex"]
const MAX_VALUE := 999999

static func validate(profiles: Dictionary) -> Dictionary:
    var errors: Array[String] = []
    for id in IDS:
        if not profiles.has(id) or typeof(profiles[id]) != TYPE_DICTIONARY:
            errors.append("missing_or_invalid_character:" + id)
            continue
        var unit: Dictionary = profiles[id]
        if typeof(unit.get("level")) != TYPE_INT or unit.get("level") != 1:
            errors.append("not_level_one:" + id)
        for field in ["max_hp", "max_mp", "mag"]:
            var value: Variant = unit.get(field)
            if typeof(value) != TYPE_INT or value < 0 or value > MAX_VALUE:
                errors.append("invalid_stat:" + id + ":" + field)
        if typeof(unit.get("max_hp")) == TYPE_INT and unit["max_hp"] <= 0:
            errors.append("nonpositive_hp:" + id)
    for id in profiles.keys():
        if typeof(id) != TYPE_STRING or id not in IDS:
            errors.append("extra_character:" + str(id))
    if not errors.is_empty():
        return {"ok": false, "errors": errors}

    for field in ["mag", "max_mp"]:
        if profiles["ender"][field] <= profiles["lyra"][field]:
            errors.append("first_second_order:" + field)
        for id in ["ionia", "reson", "aepex"]:
            if profiles["lyra"][field] <= profiles[id][field]:
                errors.append("second_remaining_order:" + field + ":" + id)

    if profiles["lyra"]["max_hp"] >= profiles["ender"]["max_hp"]:
        errors.append("hp_lowest_second_order")
    for id in ["ionia", "reson", "aepex"]:
        if profiles["ender"]["max_hp"] >= profiles[id]["max_hp"]:
            errors.append("hp_second_remaining_order:" + id)

    return {"ok": errors.is_empty(), "errors": errors}
