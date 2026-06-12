/**
 * Form validation utilities
 */

export interface ValidationError {
  field: string;
  message: string;
}

export interface ValidationResult {
  isValid: boolean;
  errors: ValidationError[];
}

/**
 * Validate email format
 */
export function isValidEmail(email: string): boolean {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
}

/**
 * Validate password strength
 */
export function validatePassword(password: string): {
  isValid: boolean;
  strength: "weak" | "fair" | "good" | "strong";
  feedback: string[];
} {
  const feedback: string[] = [];
  let strengthScore = 0;

  if (password.length < 8) {
    feedback.push("Password must be at least 8 characters");
  } else {
    strengthScore++;
  }

  if (password.length >= 12) {
    strengthScore++;
  }

  if (/[a-z]/.test(password)) {
    strengthScore++;
  } else {
    feedback.push("Add lowercase letters");
  }

  if (/[A-Z]/.test(password)) {
    strengthScore++;
  } else {
    feedback.push("Add uppercase letters");
  }

  if (/[0-9]/.test(password)) {
    strengthScore++;
  } else {
    feedback.push("Add numbers");
  }

  if (/[!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?]/.test(password)) {
    strengthScore++;
  } else {
    feedback.push("Add special characters");
  }

  let strength: "weak" | "fair" | "good" | "strong" = "weak";
  if (strengthScore >= 5) {
    strength = "strong";
  } else if (strengthScore >= 4) {
    strength = "good";
  } else if (strengthScore >= 3) {
    strength = "fair";
  }

  return {
    isValid: password.length >= 8,
    strength,
    feedback,
  };
}

/**
 * Validate login form
 */
export function validateLoginForm(email: string, password: string): ValidationResult {
  const errors: ValidationError[] = [];

  if (!email.trim()) {
    errors.push({ field: "email", message: "Email is required" });
  } else if (!isValidEmail(email)) {
    errors.push({ field: "email", message: "Please enter a valid email address" });
  }

  if (!password.trim()) {
    errors.push({ field: "password", message: "Password is required" });
  } else if (password.length < 8) {
    errors.push({ field: "password", message: "Password must be at least 8 characters" });
  }

  return {
    isValid: errors.length === 0,
    errors,
  };
}

/**
 * Validate signup form
 */
export function validateSignupForm(
  email: string,
  password: string,
  confirmPassword: string,
  fullName?: string
): ValidationResult {
  const errors: ValidationError[] = [];

  if (!email.trim()) {
    errors.push({ field: "email", message: "Email is required" });
  } else if (!isValidEmail(email)) {
    errors.push({ field: "email", message: "Please enter a valid email address" });
  }

  if (!password.trim()) {
    errors.push({ field: "password", message: "Password is required" });
  } else {
    const passwordValidation = validatePassword(password);
    if (!passwordValidation.isValid) {
      errors.push({ field: "password", message: "Password must be at least 8 characters" });
    }
  }

  if (!confirmPassword.trim()) {
    errors.push({ field: "confirmPassword", message: "Please confirm your password" });
  } else if (password !== confirmPassword) {
    errors.push({ field: "confirmPassword", message: "Passwords do not match" });
  }

  if (fullName && fullName.length > 100) {
    errors.push({ field: "fullName", message: "Name must be less than 100 characters" });
  }

  return {
    isValid: errors.length === 0,
    errors,
  };
}

/**
 * Validate reset password form
 */
export function validateResetPasswordForm(
  password: string,
  confirmPassword: string
): ValidationResult {
  const errors: ValidationError[] = [];

  if (!password.trim()) {
    errors.push({ field: "password", message: "Password is required" });
  } else {
    const passwordValidation = validatePassword(password);
    if (!passwordValidation.isValid) {
      errors.push({ field: "password", message: "Password must be at least 8 characters" });
    }
  }

  if (!confirmPassword.trim()) {
    errors.push({ field: "confirmPassword", message: "Please confirm your password" });
  } else if (password !== confirmPassword) {
    errors.push({ field: "confirmPassword", message: "Passwords do not match" });
  }

  return {
    isValid: errors.length === 0,
    errors,
  };
}

/**
 * Get error message for a specific field
 */
export function getFieldError(
  errors: ValidationError[],
  field: string
): string | undefined {
  return errors.find((e) => e.field === field)?.message;
}

/**
 * Get password strength color
 */
export function getPasswordStrengthColor(
  strength: "weak" | "fair" | "good" | "strong"
): string {
  switch (strength) {
    case "weak":
      return "text-red-500";
    case "fair":
      return "text-orange-500";
    case "good":
      return "text-yellow-500";
    case "strong":
      return "text-green-500";
    default:
      return "text-gray-500";
  }
}

/**
 * Get password strength background color
 */
export function getPasswordStrengthBgColor(
  strength: "weak" | "fair" | "good" | "strong"
): string {
  switch (strength) {
    case "weak":
      return "bg-red-500/20";
    case "fair":
      return "bg-orange-500/20";
    case "good":
      return "bg-yellow-500/20";
    case "strong":
      return "bg-green-500/20";
    default:
      return "bg-gray-500/20";
  }
}
