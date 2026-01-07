/**
 * BufferGeometryUtils - Simplified version for GLTFLoader
 * 简化版本，仅包含 GLTFLoader 需要的功能
 */

import * as THREE from './three.module.js';

/**
 * Convert TriangleStripDrawMode or TriangleFanDrawMode to TrianglesDrawMode
 * 将 TriangleStrip 或 TriangleFan 绘制模式转换为 Triangles 模式
 */
export function toTrianglesDrawMode(geometry, drawMode) {
	if (drawMode === THREE.TrianglesDrawMode) {
		console.warn('THREE.BufferGeometryUtils.toTrianglesDrawMode(): Geometry already defined as triangles.');
		return geometry;
	}

	if (drawMode === THREE.TriangleFanDrawMode || drawMode === THREE.TriangleStripDrawMode) {
		let index = geometry.getIndex();

		// Generate index if not present
		if (index === null) {
			const indices = [];
			const position = geometry.getAttribute('position');

			if (position !== undefined) {
				for (let i = 0; i < position.count; i++) {
					indices.push(i);
				}

				geometry.setIndex(indices);
				index = geometry.getIndex();
			} else {
				console.error('THREE.BufferGeometryUtils.toTrianglesDrawMode(): Undefined position attribute. Processing not possible.');
				return geometry;
			}
		}

		// Convert to triangles
		const numberOfTriangles = index.count - 2;
		const newIndices = [];

		if (drawMode === THREE.TriangleFanDrawMode) {
			// gl.TRIANGLE_FAN
			for (let i = 1; i <= numberOfTriangles; i++) {
				newIndices.push(index.getX(0));
				newIndices.push(index.getX(i));
				newIndices.push(index.getX(i + 1));
			}
		} else {
			// gl.TRIANGLE_STRIP
			for (let i = 0; i < numberOfTriangles; i++) {
				if (i % 2 === 0) {
					newIndices.push(index.getX(i));
					newIndices.push(index.getX(i + 1));
					newIndices.push(index.getX(i + 2));
				} else {
					newIndices.push(index.getX(i + 2));
					newIndices.push(index.getX(i + 1));
					newIndices.push(index.getX(i));
				}
			}
		}

		if ((newIndices.length / 3) !== numberOfTriangles) {
			console.error('THREE.BufferGeometryUtils.toTrianglesDrawMode(): Unable to generate correct amount of triangles.');
		}

		// Build final geometry
		const newGeometry = geometry.clone();
		newGeometry.setIndex(newIndices);
		newGeometry.drawRange.start = 0;
		newGeometry.drawRange.count = Infinity;

		return newGeometry;
	} else {
		console.error('THREE.BufferGeometryUtils.toTrianglesDrawMode(): Unknown draw mode:', drawMode);
		return geometry;
	}
}

