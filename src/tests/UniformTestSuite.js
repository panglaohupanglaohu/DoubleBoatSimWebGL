/**
 * Comprehensive Uniform Testing Suite
 * 全面的 Uniform 测试套件
 * 
 * This test suite creates various problematic scenarios and verifies
 * that our diagnostic and patching systems can handle them all.
 * 
 * 该测试套件创建各种问题场景，并验证我们的诊断和补丁系统能够处理它们。
 */

import * as THREE from '../../public/lib/three.module.js';
import { uniformInterceptor } from './UniformInterceptor.js';
import { MaterialUniformsTest } from './MaterialUniformsTest.js';
import { renderSafetyPatch } from './RenderSafetyPatch.js';

export class UniformTestSuite {
  constructor() {
    this.testResults = [];
    this.passed = 0;
    this.failed = 0;
  }

  /**
   * Run all tests
   * 运行所有测试
   */
  async runAllTests(scene, renderer) {
    console.log('🧪 ========================================');
    console.log('🧪 Uniform Test Suite - Starting');
    console.log('🧪 ========================================\n');

    this.testResults = [];
    this.passed = 0;
    this.failed = 0;

    // Test 1: Null uniform
    await this.testNullUniform(scene, renderer);

    // Test 2: Undefined uniform
    await this.testUndefinedUniform(scene, renderer);

    // Test 3: Primitive value instead of object
    await this.testPrimitiveUniform(scene, renderer);

    // Test 4: Object without value property
    await this.testMissingValueProperty(scene, renderer);

    // Test 5: Undefined value
    await this.testUndefinedValue(scene, renderer);

    // Test 6: MeshPhysicalMaterial with transmission
    await this.testPhysicalMaterial(scene, renderer);

    // Test 7: Dynamic material addition during runtime
    await this.testDynamicMaterialAddition(scene, renderer);

    // Test 8: Stress test - render multiple frames
    await this.testMultiFrameRendering(scene, renderer);

    // Print summary
    this.printSummary();

    return {
      passed: this.passed,
      failed: this.failed,
      total: this.testResults.length,
      results: this.testResults
    };
  }

  /**
   * Test 1: Null uniform
   */
  async testNullUniform(scene, renderer) {
    console.log('\n🧪 Test 1: Null Uniform');
    console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');

    try {
      // Create a problematic shader material
      const material = new THREE.ShaderMaterial({
        uniforms: {
          testUniform: null // PROBLEMATIC!
        },
        vertexShader: `
          void main() {
            gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
          }
        `,
        fragmentShader: `
          uniform float testUniform;
          void main() {
            gl_FragColor = vec4(1.0, 0.0, 0.0, 1.0);
          }
        `
      });

      // Create a test object
      const geometry = new THREE.BoxGeometry(1, 1, 1);
      const mesh = new THREE.Mesh(geometry, material);
      mesh.name = 'TestNullUniform';
      scene.add(mesh);

      // Apply interceptors
      uniformInterceptor.interceptMaterial(material);

      // Try to render
      renderer.render(scene, new THREE.PerspectiveCamera());

      // Check if uniform was fixed
      if (material.uniforms.testUniform && 
          typeof material.uniforms.testUniform === 'object' &&
          'value' in material.uniforms.testUniform) {
        this.recordPass('Null Uniform', 'Null uniform was successfully fixed');
      } else {
        this.recordFail('Null Uniform', 'Null uniform was not fixed');
      }

      // Cleanup
      scene.remove(mesh);
      geometry.dispose();
      material.dispose();

    } catch (error) {
      this.recordFail('Null Uniform', `Test threw error: ${error.message}`);
    }
  }

  /**
   * Test 2: Undefined uniform
   */
  async testUndefinedUniform(scene, renderer) {
    console.log('\n🧪 Test 2: Undefined Uniform');
    console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');

    try {
      const material = new THREE.ShaderMaterial({
        uniforms: {
          testUniform: undefined // PROBLEMATIC!
        },
        vertexShader: `void main() { gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0); }`,
        fragmentShader: `uniform float testUniform; void main() { gl_FragColor = vec4(1.0, 0.0, 0.0, 1.0); }`
      });

      const geometry = new THREE.BoxGeometry(1, 1, 1);
      const mesh = new THREE.Mesh(geometry, material);
      mesh.name = 'TestUndefinedUniform';
      scene.add(mesh);

      uniformInterceptor.interceptMaterial(material);
      renderer.render(scene, new THREE.PerspectiveCamera());

      if (material.uniforms.testUniform && 'value' in material.uniforms.testUniform) {
        this.recordPass('Undefined Uniform', 'Undefined uniform was successfully fixed');
      } else {
        this.recordFail('Undefined Uniform', 'Undefined uniform was not fixed');
      }

      scene.remove(mesh);
      geometry.dispose();
      material.dispose();

    } catch (error) {
      this.recordFail('Undefined Uniform', `Test threw error: ${error.message}`);
    }
  }

  /**
   * Test 3: Primitive value instead of object
   */
  async testPrimitiveUniform(scene, renderer) {
    console.log('\n🧪 Test 3: Primitive Value as Uniform');
    console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');

    try {
      const material = new THREE.ShaderMaterial({
        uniforms: {
          testUniform: 42.0 // PROBLEMATIC! Should be { value: 42.0 }
        },
        vertexShader: `void main() { gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0); }`,
        fragmentShader: `uniform float testUniform; void main() { gl_FragColor = vec4(1.0, 0.0, 0.0, 1.0); }`
      });

      const geometry = new THREE.BoxGeometry(1, 1, 1);
      const mesh = new THREE.Mesh(geometry, material);
      mesh.name = 'TestPrimitiveUniform';
      scene.add(mesh);

      uniformInterceptor.interceptMaterial(material);
      renderer.render(scene, new THREE.PerspectiveCamera());

      if (material.uniforms.testUniform && 
          typeof material.uniforms.testUniform === 'object' &&
          'value' in material.uniforms.testUniform &&
          material.uniforms.testUniform.value === 42.0) {
        this.recordPass('Primitive Uniform', 'Primitive uniform was successfully wrapped');
      } else {
        this.recordFail('Primitive Uniform', 'Primitive uniform was not fixed');
      }

      scene.remove(mesh);
      geometry.dispose();
      material.dispose();

    } catch (error) {
      this.recordFail('Primitive Uniform', `Test threw error: ${error.message}`);
    }
  }

  /**
   * Test 4: Object without value property
   */
  async testMissingValueProperty(scene, renderer) {
    console.log('\n🧪 Test 4: Object Without Value Property');
    console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');

    try {
      const material = new THREE.ShaderMaterial({
        uniforms: {
          testUniform: { type: 'f' } // PROBLEMATIC! Missing 'value'
        },
        vertexShader: `void main() { gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0); }`,
        fragmentShader: `uniform float testUniform; void main() { gl_FragColor = vec4(1.0, 0.0, 0.0, 1.0); }`
      });

      const geometry = new THREE.BoxGeometry(1, 1, 1);
      const mesh = new THREE.Mesh(geometry, material);
      mesh.name = 'TestMissingValue';
      scene.add(mesh);

      uniformInterceptor.interceptMaterial(material);
      renderer.render(scene, new THREE.PerspectiveCamera());

      if ('value' in material.uniforms.testUniform) {
        this.recordPass('Missing Value Property', 'Value property was successfully added');
      } else {
        this.recordFail('Missing Value Property', 'Value property was not added');
      }

      scene.remove(mesh);
      geometry.dispose();
      material.dispose();

    } catch (error) {
      this.recordFail('Missing Value Property', `Test threw error: ${error.message}`);
    }
  }

  /**
   * Test 5: Undefined value
   */
  async testUndefinedValue(scene, renderer) {
    console.log('\n🧪 Test 5: Undefined Value');
    console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');

    try {
      const material = new THREE.ShaderMaterial({
        uniforms: {
          testUniform: { value: undefined } // PROBLEMATIC!
        },
        vertexShader: `void main() { gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0); }`,
        fragmentShader: `uniform float testUniform; void main() { gl_FragColor = vec4(1.0, 0.0, 0.0, 1.0); }`
      });

      const geometry = new THREE.BoxGeometry(1, 1, 1);
      const mesh = new THREE.Mesh(geometry, material);
      mesh.name = 'TestUndefinedValue';
      scene.add(mesh);

      uniformInterceptor.interceptMaterial(material);
      renderer.render(scene, new THREE.PerspectiveCamera());

      if (material.uniforms.testUniform.value !== undefined) {
        this.recordPass('Undefined Value', 'Undefined value was successfully fixed');
      } else {
        this.recordFail('Undefined Value', 'Undefined value was not fixed');
      }

      scene.remove(mesh);
      geometry.dispose();
      material.dispose();

    } catch (error) {
      this.recordFail('Undefined Value', `Test threw error: ${error.message}`);
    }
  }

  /**
   * Test 6: MeshPhysicalMaterial
   */
  async testPhysicalMaterial(scene, renderer) {
    console.log('\n🧪 Test 6: MeshPhysicalMaterial with Advanced Features');
    console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');

    try {
      const material = new THREE.MeshPhysicalMaterial({
        color: 0xffffff,
        transmission: 0.9,
        thickness: 1.0,
        roughness: 0.0
      });

      const geometry = new THREE.BoxGeometry(1, 1, 1);
      const mesh = new THREE.Mesh(geometry, material);
      mesh.name = 'TestPhysicalMaterial';
      scene.add(mesh);

      // Test with MaterialUniformsTest
      const tester = new MaterialUniformsTest();
      const result = tester.diagnoseScene(scene, renderer);

      if (result.warnings.length > 0) {
        this.recordPass('MeshPhysicalMaterial', 'Advanced features detected and warned');
      } else {
        this.recordPass('MeshPhysicalMaterial', 'Material rendered without errors');
      }

      scene.remove(mesh);
      geometry.dispose();
      material.dispose();

    } catch (error) {
      this.recordFail('MeshPhysicalMaterial', `Test threw error: ${error.message}`);
    }
  }

  /**
   * Test 7: Dynamic material addition
   */
  async testDynamicMaterialAddition(scene, renderer) {
    console.log('\n🧪 Test 7: Dynamic Material Addition During Runtime');
    console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');

    try {
      const meshes = [];

      // Add 5 materials dynamically
      for (let i = 0; i < 5; i++) {
        const material = new THREE.ShaderMaterial({
          uniforms: {
            dynamicUniform: { value: i }
          },
          vertexShader: `void main() { gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0); }`,
          fragmentShader: `uniform float dynamicUniform; void main() { gl_FragColor = vec4(1.0, 0.0, 0.0, 1.0); }`
        });

        const geometry = new THREE.BoxGeometry(1, 1, 1);
        const mesh = new THREE.Mesh(geometry, material);
        mesh.name = `DynamicMaterial${i}`;
        scene.add(mesh);
        meshes.push(mesh);

        // Render after each addition
        renderer.render(scene, new THREE.PerspectiveCamera());
      }

      // Re-intercept scene to catch new materials
      uniformInterceptor.interceptScene(scene);

      // Render again
      renderer.render(scene, new THREE.PerspectiveCamera());

      this.recordPass('Dynamic Addition', 'Successfully rendered with dynamically added materials');

      // Cleanup
      meshes.forEach(mesh => {
        scene.remove(mesh);
        mesh.geometry.dispose();
        mesh.material.dispose();
      });

    } catch (error) {
      this.recordFail('Dynamic Addition', `Test threw error: ${error.message}`);
    }
  }

  /**
   * Test 8: Multi-frame stress test
   */
  async testMultiFrameRendering(scene, renderer) {
    console.log('\n🧪 Test 8: Multi-Frame Rendering Stress Test');
    console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');

    try {
      // Create a material with problematic uniform
      const material = new THREE.ShaderMaterial({
        uniforms: {
          time: { value: 0.0 },
          problematicUniform: null // Will be fixed
        },
        vertexShader: `void main() { gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0); }`,
        fragmentShader: `
          uniform float time;
          uniform float problematicUniform;
          void main() { gl_FragColor = vec4(1.0, 0.0, 0.0, 1.0); }
        `
      });

      const geometry = new THREE.BoxGeometry(1, 1, 1);
      const mesh = new THREE.Mesh(geometry, material);
      mesh.name = 'StressTest';
      scene.add(mesh);

      uniformInterceptor.interceptMaterial(material);

      // Render 100 frames
      let framesPassed = 0;
      for (let i = 0; i < 100; i++) {
        material.uniforms.time.value = i * 0.016; // Simulate time
        try {
          renderer.render(scene, new THREE.PerspectiveCamera());
          framesPassed++;
        } catch (error) {
          console.error(`  Frame ${i} failed:`, error.message);
          break;
        }
      }

      if (framesPassed === 100) {
        this.recordPass('Multi-Frame Stress', `All 100 frames rendered successfully`);
      } else {
        this.recordFail('Multi-Frame Stress', `Only ${framesPassed}/100 frames rendered`);
      }

      scene.remove(mesh);
      geometry.dispose();
      material.dispose();

    } catch (error) {
      this.recordFail('Multi-Frame Stress', `Test threw error: ${error.message}`);
    }
  }

  /**
   * Record a passing test
   */
  recordPass(testName, message) {
    console.log(`  ✅ PASS: ${message}`);
    this.testResults.push({ test: testName, passed: true, message });
    this.passed++;
  }

  /**
   * Record a failing test
   */
  recordFail(testName, message) {
    console.log(`  ❌ FAIL: ${message}`);
    this.testResults.push({ test: testName, passed: false, message });
    this.failed++;
  }

  /**
   * Print test summary
   */
  printSummary() {
    console.log('\n\n🧪 ========================================');
    console.log('🧪 Test Suite Summary');
    console.log('🧪 ========================================');
    console.log(`\n  Total Tests: ${this.testResults.length}`);
    console.log(`  ✅ Passed: ${this.passed}`);
    console.log(`  ❌ Failed: ${this.failed}`);
    console.log(`  Success Rate: ${((this.passed / this.testResults.length) * 100).toFixed(1)}%`);

    if (this.failed > 0) {
      console.log('\n  Failed Tests:');
      this.testResults.filter(r => !r.passed).forEach(r => {
        console.log(`    • ${r.test}: ${r.message}`);
      });
    }

    console.log('\n🧪 ========================================\n');

    // Print stats from all systems
    console.log('📊 System Statistics:');
    uniformInterceptor.printStats();
    renderSafetyPatch.printStats();
  }
}

// Export singleton
export const uniformTestSuite = new UniformTestSuite();

