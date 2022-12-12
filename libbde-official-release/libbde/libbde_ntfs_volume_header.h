/*
 * The NTFS volume header functions
 *
 * Copyright (C) 2011-2022, Joachim Metz <joachim.metz@gmail.com>
 *
 * Refer to AUTHORS for acknowledgements.
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU Lesser General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU Lesser General Public License
 * along with this program.  If not, see <https://www.gnu.org/licenses/>.
 */

#if !defined( _LIBBDE_NTFS_VOLUME_HEADER_H )
#define _LIBBDE_NTFS_VOLUME_HEADER_H

#include <common.h>
#include <types.h>

#include "libbde_libcerror.h"

#if defined( __cplusplus )
extern "C" {
#endif

typedef struct libbde_ntfs_volume_header libbde_ntfs_volume_header_t;

struct libbde_ntfs_volume_header
{
	/* The number of bytes per sector
	 */
	uint16_t bytes_per_sector;

	/* The volume size
	 */
	size64_t volume_size;
};

int libbde_ntfs_volume_header_initialize(
     libbde_ntfs_volume_header_t **ntfs_volume_header,
     libcerror_error_t **error );

int libbde_ntfs_volume_header_free(
     libbde_ntfs_volume_header_t **ntfs_volume_header,
     libcerror_error_t **error );

int libbde_ntfs_volume_header_read_data(
     libbde_ntfs_volume_header_t *ntfs_volume_header,
     const uint8_t *data,
     size_t data_size,
     libcerror_error_t **error );

#if defined( __cplusplus )
}
#endif

#endif /* !defined( _LIBBDE_NTFS_VOLUME_HEADER_H ) */

