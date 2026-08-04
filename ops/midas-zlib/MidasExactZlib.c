#define WIN32_LEAN_AND_MEAN
#include <windows.h>
#include <stdint.h>
#include "zlib.h"

#ifdef __cplusplus
extern "C" {
#endif

__declspec(dllexport) int __stdcall MidasZlib9Size(const unsigned char *data, int length)
{
    if (data == NULL || length < 0) return -1;
    uLongf out_len = compressBound((uLong)length);
    Bytef *out = (Bytef*)HeapAlloc(GetProcessHeap(), 0, (SIZE_T)out_len);
    if (out == NULL) return -2;
    int rc = compress2(out, &out_len, (const Bytef*)data, (uLong)length, Z_BEST_COMPRESSION);
    HeapFree(GetProcessHeap(), 0, out);
    if (rc != Z_OK || out_len > INT32_MAX) return -1000 - rc;
    return (int)out_len;
}

__declspec(dllexport) int __stdcall MidasZlibVersionCheck(void)
{
    const char *v = zlibVersion();
    return (v != NULL && v[0] == '1') ? 131 : -1;
}

BOOL WINAPI DllMain(HINSTANCE hinstDLL, DWORD fdwReason, LPVOID lpReserved)
{
    (void)hinstDLL; (void)fdwReason; (void)lpReserved;
    return TRUE;
}

#ifdef __cplusplus
}
#endif
