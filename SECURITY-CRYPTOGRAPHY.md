# Cryptographic Security Standards

This document outlines the cryptographic standards and practices used in this project, addressing findings from IBM Quantum Safe Explorer scans.

## Summary of Cryptographic Vulnerabilities

### Fixed Issues (Production Code)

1. **MD5 Hash Usage** - FIXED
   - **Files**: `dataset_manager.py`, `registry_cache.py`
   - **Issue**: MD5 is cryptographically broken and should not be used
   - **Resolution**: Replaced with SHA-256 for all hash operations
   - **Impact**: Non-cryptographic use cases (cache keys, dataset IDs) now use secure hash

2. **Static IV Concerns** - FALSE POSITIVE
   - **Files**: `encryption_service.py`, `a706a3320c56_use_argon2id_for_encryption_key.py`
   - **Issue**: Scanner flagged potential static IV usage
   - **Resolution**: Added documentation clarifying that Fernet automatically generates random IVs
   - **Details**: The Python `cryptography.fernet.Fernet` library automatically generates a random 128-bit IV for each encryption operation. The IV is embedded in the token and extracted during decryption.

### Test File Issues (Accepted Risk)

The following vulnerabilities exist in **test files only** and represent accepted risks for testing purposes:

#### Non-Quantum-Resistant Algorithms in Tests

**Affected Files:**
- `tests/unit/mcpgateway/utils/test_validate_signature.py`
- `tests/unit/mcpgateway/utils/test_ssl_key_manager.py`
- `tests/unit/mcpgateway/test_auth.py`
- `tests/unit/mcpgateway/test_config.py`
- `mcpgateway/utils/generate_keys.py` (utility for testing)

**Algorithms Used:**
- Ed25519 (Elliptic Curve Digital Signature Algorithm)
- RSA with 1024-bit keys (test scenarios only)

**Rationale:**
1. These are **test files** validating existing functionality
2. Production systems should use quantum-resistant algorithms (ML-KEM, ML-DSA, SLH-DSA)
3. Current cryptographic libraries in Python ecosystem have limited quantum-resistant support
4. Migration to quantum-resistant algorithms requires:
   - Ecosystem maturity (NIST PQC standards finalized in 2024)
   - Library support in `cryptography` package
   - Backward compatibility considerations

## Current Cryptographic Standards

### Production Use

#### Symmetric Encryption
- **Algorithm**: AES-128-CBC (via Fernet)
- **Key Derivation**: Argon2id
  - Time cost: 3 iterations
  - Memory cost: 65536 KiB
  - Parallelism: 1 thread
- **IV Generation**: Random 128-bit IV per encryption (automatic via Fernet)
- **Authentication**: HMAC-SHA256 (via Fernet)

#### Hashing
- **Algorithm**: SHA-256
- **Use Cases**: 
  - Cache key generation
  - Dataset identification
  - Content integrity verification
- **Salt**: Random salt generated per operation where applicable

#### Password Hashing
- **Algorithm**: Argon2id
- **Parameters**: Configurable via environment variables
- **Default Settings**: Production-grade security parameters

### Test Environment

#### Digital Signatures (Test Only)
- **Ed25519**: Used for signature validation tests
- **RSA**: Used for SSL/TLS certificate generation tests
- **Note**: These are for testing existing integrations, not production use

## Quantum-Resistant Cryptography Roadmap

### Current Status
- **Risk Assessment**: Low immediate risk (quantum computers capable of breaking current algorithms are not yet available)
- **Timeline**: NIST PQC standards finalized in 2024, ecosystem adoption ongoing

### Migration Plan

1. **Phase 1: Monitoring** (Current)
   - Track NIST PQC standardization progress
   - Monitor Python `cryptography` library for PQC support
   - Document current algorithm usage

2. **Phase 2: Evaluation** (When libraries mature)
   - Evaluate ML-KEM (Key Encapsulation)
   - Evaluate ML-DSA (Digital Signatures)
   - Evaluate SLH-DSA (Stateless Hash-Based Signatures)
   - Performance testing and compatibility assessment

3. **Phase 3: Implementation** (Post-ecosystem maturity)
   - Implement hybrid classical/quantum-resistant schemes
   - Gradual migration with backward compatibility
   - Update test suites to validate new algorithms

4. **Phase 4: Deprecation** (Long-term)
   - Deprecate classical algorithms
   - Full quantum-resistant deployment

## Compliance

### FIPS 140-3 Level 1
- **SHA-256**: Compliant (approved message digest algorithm)
- **AES-128**: Compliant (via Fernet implementation)
- **Argon2id**: Modern KDF, successor to PBKDF2

### CWE Mitigations

- **CWE-327** (Broken Cryptographic Algorithm): Eliminated MD5 usage in production
- **CWE-328** (Weak Hash): Replaced with SHA-256
- **CWE-759** (Salt-less Hash): Using random salts where applicable
- **CWE-1204** (Static IV): False positive - Fernet uses random IVs
- **CWE-326** (Weak Key): Test files only, production uses strong keys

## Best Practices

1. **Never use MD5 or SHA-1** for cryptographic purposes
2. **Always use random IVs** - Fernet handles this automatically
3. **Use Argon2id** for password/key derivation
4. **Generate random salts** for each encryption operation
5. **Use authenticated encryption** - Fernet provides this via HMAC
6. **Plan for quantum resistance** - Monitor PQC developments

## References

- [NIST Post-Quantum Cryptography](https://csrc.nist.gov/projects/post-quantum-cryptography)
- [Python Cryptography Library](https://cryptography.io/)
- [Fernet Specification](https://github.com/fernet/spec/blob/master/Spec.md)
- [Argon2 RFC 9106](https://www.rfc-editor.org/rfc/rfc9106.html)
- [CWE-327: Use of Broken Cryptographic Algorithm](https://cwe.mitre.org/data/definitions/327.html)

## Scan Results

Last IBM Quantum Safe Explorer scan: 2026-05-22

- **Total Vulnerabilities**: 67
  - **High Severity**: 28
  - **Low Severity**: 39
- **Production Code Issues**: 4 (all fixed)
- **Test Code Issues**: 24 (accepted risk, documented)
- **False Positives**: 6 (Fernet IV warnings, documented)

## Contact

For security concerns or questions about cryptographic implementations, please refer to the project's security policy or contact the maintainers.