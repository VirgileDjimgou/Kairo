class MemberProfile {
  const MemberProfile({
    required this.id,
    required this.memberCode,
    required this.firstName,
    required this.lastName,
    required this.displayName,
    required this.status,
    required this.membershipType,
    required this.joinedAt,
    this.email,
    this.phone,
    this.streetName,
    this.houseNumber,
    this.postalCode,
    this.city,
    this.countryCode,
  });

  factory MemberProfile.fromJson(Map<String, dynamic> json) => MemberProfile(
    id: json['id'] as String,
    memberCode: json['member_code'] as String,
    firstName: json['first_name'] as String,
    lastName: json['last_name'] as String,
    displayName: json['display_name'] as String,
    email: json['email'] as String?,
    phone: json['phone'] as String?,
    streetName: json['street_name'] as String?,
    houseNumber: json['house_number'] as String?,
    postalCode: json['postal_code'] as String?,
    city: json['city'] as String?,
    countryCode: json['country_code'] as String?,
    status: json['status'] as String? ?? 'active',
    membershipType: json['membership_type'] as String? ?? 'individual',
    joinedAt: DateTime.tryParse(json['joined_at'] as String? ?? ''),
  );

  final String id;
  final String memberCode;
  final String firstName;
  final String lastName;
  final String displayName;
  final String? email;
  final String? phone;
  final String? streetName;
  final String? houseNumber;
  final String? postalCode;
  final String? city;
  final String? countryCode;
  final String status;
  final String membershipType;
  final DateTime? joinedAt;

  String get address => <String?>[
    if (streetName != null) '$streetName ${houseNumber ?? ''}'.trim(),
    if (postalCode != null || city != null)
      '${postalCode ?? ''} ${city ?? ''}'.trim(),
    countryCode,
  ].whereType<String>().where((String value) => value.isNotEmpty).join(', ');
}

class MemberDraft {
  const MemberDraft({
    required this.firstName,
    required this.lastName,
    required this.displayName,
    required this.streetName,
    required this.houseNumber,
    required this.postalCode,
    required this.city,
    required this.countryCode,
    required this.membershipType,
    this.phone,
    this.provisionAccess = false,
    this.loginIdentifier,
    this.temporaryPassword,
  });

  final String firstName;
  final String lastName;
  final String displayName;
  final String streetName;
  final String houseNumber;
  final String postalCode;
  final String city;
  final String countryCode;
  final String membershipType;
  final String? phone;
  final bool provisionAccess;
  final String? loginIdentifier;
  final String? temporaryPassword;

  Map<String, dynamic> toJson() => <String, dynamic>{
    'first_name': firstName.trim(),
    'last_name': lastName.trim(),
    'display_name': displayName.trim(),
    'street_name': streetName.trim(),
    'house_number': houseNumber.trim(),
    'postal_code': postalCode.trim(),
    'city': city.trim(),
    'country_code': countryCode.trim().toUpperCase(),
    'membership_type': membershipType,
    if (phone != null && phone!.trim().isNotEmpty) 'phone': phone!.trim(),
    'provision_access': provisionAccess,
    if (provisionAccess &&
        loginIdentifier != null &&
        loginIdentifier!.trim().isNotEmpty)
      'login_identifier': loginIdentifier!.trim(),
    if (provisionAccess && temporaryPassword != null)
      'temporary_password': temporaryPassword,
  };
}
